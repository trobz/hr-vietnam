# -*- coding: utf-8 -*-
# Copyright 2009-2018 Trobz (http://trobz.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime

from odoo import models, api
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    @api.model
    def _get_total_working_days(self, payslip, code='WorkingDays'):
        res = 0
        for line in payslip.worked_days_line_ids:
            if line.code == code:
                res += line.number_of_days
        return res

    @api.model
    def _get_base_date(self, d, day_nb):
        base_date = datetime.strptime(d, DF).strftime('%Y-%m-' + str(day_nb))
        return base_date

    @api.multi
    def _get_wage_by_base_date(self, contract, payslip, day_nb=15):
        hr_payslip = self.env['hr.payslip']
        base_date = self._get_base_date(payslip.date_to, day_nb)
        contract_ids = hr_payslip.get_contract(self, base_date, base_date)
        if contract.id not in contract_ids:
            return 0.0
        return contract.wage
