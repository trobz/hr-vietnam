# -*- coding: utf-8 -*-
# Copyright 2009-2018 Trobz (http://trobz.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import date
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF


class HrHolidays(models.Model):
    _inherit = 'hr.holidays'

    @api.model
    def compute_allo_days(self, employee_id, hol_status_ids,
                          date_from=False, date_to=False):
        """
        Calculate the allocation request which was approved
        """
        if not hol_status_ids:
            return 0
        sql = """
            SELECT
                CASE
                    WHEN SUM(h.number_of_days) > 0 THEN SUM(h.number_of_days)
                    ELSE 0
                END as allo_days
                FROM
                    hr_holidays h
                    join hr_holidays_status s on (s.id=h.holiday_status_id)
                WHERE
                    h.type='add' AND
                    h.state='validate' AND
                    s.limit=False AND
                    h.employee_id = %s AND
                    h.holiday_status_id in (%s)
            """ % (employee_id, ','.join(map(str, hol_status_ids)),)
        if date_from and date_to:
            sql += """ AND h.allo_date >= '%s'
                           AND h.time_of_allocation_date <= '%s'
                           """ % (date_from, date_to)
        elif not date_from and date_to:
            sql += " AND h.allo_date <= '%s'" % (date_to)
        elif date_from and not date_to:
            sql += " AND h.allo_date >= '%s'" % (date_from)
        self._cr.execute(sql)
        res = self._cr.fetchone()
        return res and res[0] or 0

    @api.model
    def compute_leave_days(
            self, employee_id, holiday_status_ids,
            date_from=False, date_to=False):
        """
        Calculate number of leave days of a given employee and given period
        - If not date_to, get from date_from to today
        """
        holidays = self.browse()
        # No given leave type
        if not holiday_status_ids:
            return 0, False
        domain = [('employee_id', '=', employee_id),
                  ('state', '=', 'validate'),
                  ('type', '=', 'remove'),
                  ('holiday_status_id', 'in', holiday_status_ids)]
        if not date_to:
            date_to = date.today().strftime(DF)

        if date_from and date_to:
            # vacation_date_from > date from and vacation_date_to < date to
            inner_holidays = self.search(
                domain + [('vacation_date_from', '>', date_from),
                          ('vacation_date_to', '<', date_to)])
            leave_days = sum([x.number_of_days_temp for x in inner_holidays])
            # vacation_date_from <= date from and vacation_date_to >= date from
            # OR vacation_date_from <= date to and vacation_date_to >= date to
            outer_holidays = self.search(
                domain + ['|', '&', ('vacation_date_from', '<=', date_from),
                          ('vacation_date_to', '>=', date_from),
                          '&', ('vacation_date_from', '<=', date_to),
                          ('vacation_date_to', '>=', date_to)])
            if not outer_holidays:
                return leave_days, inner_holidays
            holidays = inner_holidays + outer_holidays
            # Get country of the employee company
            employee = self.env['hr.employee'].browse(employee_id)
            company = employee.company_id
            country_id = False
            if company and company.country_id:
                country_id = company.country_id.id
            hr_payslip = self.env['hr.payslip']
            hr_contract = self.env['hr.contract']
            for hol in outer_holidays:
                number_of_days = 0
                resource_calendar_id = None
                vacation_date_from = hol.vacation_date_from
                vacation_date_to = hol.vacation_date_to
                vacation_date_from_dt = fields.Date.from_string(
                    vacation_date_from)
                vacation_date_to_dt = fields.Date.from_string(
                    vacation_date_to)
                date_dt = date_from_dt = fields.Date.from_string(
                    max(vacation_date_from, date_from))
                date_to_dt = fields.Date.from_string(
                    min(vacation_date_to, date_to))
                # get valid contract of this leave request
                contract_ids = hr_payslip.get_contract(
                    employee, vacation_date_from, vacation_date_to)
                if contract_ids:
                    contract = hr_contract.browse(contract_ids[-1])
                    if contract.resource_calendar_id:
                        resource_calendar_id = contract.resource_calendar_id.id

                # Stating time and ending time is the same
                if hol.number_of_days_temp == 0:
                    number_of_days = 0
                # Stating time and ending time is different
                vacation_time_from = hol.vacation_time_from
                vacation_time_to = hol.vacation_time_to
                while date_dt <= date_to_dt:
                    if date_dt == date_from_dt == vacation_date_from_dt:
                        day = vacation_time_from == 'morning' and 1 or 0.5
                        date_type = vacation_time_from == 'morning' and \
                            'full' or 'afternoon'
                    elif date_dt == date_to_dt == vacation_date_to_dt:
                        day = vacation_time_to == 'evening' and 1 or 0.5
                        date_type = vacation_time_to == 'evening' and 'full' \
                            or 'morning'
                    else:
                        day = 1
                        date_type = 'full'
                    number_of_days += self.plus_day(
                        resource_calendar_id, date_dt, day, date_type,
                        country_id)
                    date_dt = date_dt + relativedelta(days=1)
                leave_days += number_of_days
        else:
            # If not date_from or not date_to
            # Get all leave requests of this employee
            holidays = self.search(domain)
            leave_days = sum([x.number_of_days_temp for x in holidays])
        return leave_days, holidays
