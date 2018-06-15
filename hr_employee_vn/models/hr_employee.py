# -*- coding: utf-8 -*-
# Copyright 2009-2018 Trobz (http://trobz.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime

from dateutil import relativedelta

from odoo import api, fields, models
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    def _get_ethnic_group(self):
        ethnic_group = self.env['ethnic.group'].search(
            [('is_default', '=', True)])
        return ethnic_group and ethnic_group.ids[0] or False

    @api.depends('birthday')
    def _compute_age(self):
        for employee in self:
            if employee.birthday:
                birthday_year = fields.Datetime.from_string(
                    employee.birthday).year
                current_day = fields.Date.context_today(self)
                current_year = fields.Datetime.from_string(current_day).year
                employee.age = current_year - birthday_year

    @api.depends('family_ids')
    def _compute_number_of_dependent(self):
        for employee in self:
            employee.number_of_dependent = len(employee.family_ids.filtered(
                lambda f: f.dependent).ids)

    def _calc_work_seniority_month(self):
        for obj in self:
            if obj.hire_date:
                to_dt = datetime.now()
                if obj.contract_ended_date:
                    contract_ended_date = datetime.strptime(
                        obj.contract_ended_date, DEFAULT_SERVER_DATE_FORMAT)
                    if to_dt > contract_ended_date:
                        to_dt = contract_ended_date

                from_dt = datetime.strptime(
                    obj.hire_date, DEFAULT_SERVER_DATE_FORMAT)
                data = relativedelta.relativedelta(to_dt, from_dt)
                obj.work_seniority_month = data.months + data.years * 12

    number = fields.Char("Number", default='/', readonly=True)
    age = fields.Integer("Age", compute="_compute_age")
    ethnic_group_id = fields.Many2one(
        "ethnic.group",
        "Ethnic Group",
        default=_get_ethnic_group)
    religion = fields.Char("Religion")
    # Hometown
    hometown_address = fields.Char('Address')
    hometown_ward_id = fields.Many2one(
        "res.country.state.district.ward",
        "Commune/Ward",
        domain="[('district_id', '=', hometown_district_id)]")
    hometown_district_id = fields.Many2one(
        "res.country.state.district",
        "District",
        domain="[('state_id', '=', hometown_state_id)]")
    hometown_state_id = fields.Many2one(
        "res.country.state",
        "Province/City",
        domain="[('country_id', '=', hometown_country_id)]")
    hometown_country_id = fields.Many2one("res.country", "Country")

    # Resident address
    resident_address = fields.Char('Address')
    resident_ward_id = fields.Many2one(
        "res.country.state.district.ward",
        "Commune/Ward",
        domain="[('district_id', '=', resident_district_id)]")
    resident_district_id = fields.Many2one(
        "res.country.state.district",
        "District",
        domain="[('state_id', '=', resident_state_id)]")
    resident_state_id = fields.Many2one(
        "res.country.state",
        "Province/City",
        domain="[('country_id', '=', resident_country_id)]")
    resident_country_id = fields.Many2one("res.country", "Country")

    # Current address
    current_address = fields.Char('Address')
    current_ward_id = fields.Many2one(
        "res.country.state.district.ward",
        "Commune/Ward",
        domain="[('district_id', '=', current_district_id)]")
    current_district_id = fields.Many2one(
        "res.country.state.district",
        "District",
        domain="[('state_id', '=', current_state_id)]")
    current_state_id = fields.Many2one(
        "res.country.state",
        "Province/City",
        domain="[('country_id', '=', current_country_id)]")
    current_country_id = fields.Many2one("res.country", "Country")

    private_email = fields.Char('Private Email')
    skype = fields.Char("Skype")

    id_date_issue = fields.Date("ID Issue Date")
    id_place_issue_id = fields.Many2one("res.country.state", "ID Issue Place")

    bank_ids = fields.One2many(
        'hr.employee.bank',
        'employee_id',
        'Bank Accounts')
    family_ids = fields.One2many(
        'hr.employee.family',
        'employee_id',
        'Family Information')
    number_of_dependent = fields.Integer(
        'Number of Dependents',
        compute="_compute_number_of_dependent")
    education_ids = fields.One2many(
        'hr.employee.education',
        'employee_id',
        'Education')
    work_permit_expire_date = fields.Date("Work Permit Expire Date")

    # --Work Information
    job_level_id = fields.Many2one("hr.job.level", "Job Level")
    started_date = fields.Date("Started Date")
    hire_date = fields.Date("Hired Date")
    contract_ended_date = fields.Date("Contract ended")
    work_seniority_month = fields.Integer(
        "Work Seniority Month",
        compute='_calc_work_seniority_month',
        readonly=True)
    social_insurance_no = fields.Char("Social Insurance No")
    insurance_date_issue = fields.Date("Date of Issue")
    insurance_date_return = fields.Date("Date of Return")
    insurance_other_place = fields.Boolean("Other Place")
    health_insurance_no = fields.Char("Health Insurance No")
    is_union = fields.Boolean("Union fee")

    # --Job Position History
    position_history_ids = fields.One2many(
        'hr.position.history',
        'employee_id',
        'Job Position History')

    @api.model
    def create(self, vals):
        if vals.get('number', '/') == '/':
            vals['number'] = self.env['ir.sequence'].next_by_code(
                'hr.employee.number')
        res = super(HrEmployee, self).create(vals)
        return res

    @api.multi
    def write(self, vals):
        lst_job = {}
        if vals.get('job_id'):
            for employee in self:
                lst_job.update({employee: employee.job_id})

        res = super(HrEmployee, self).write(vals)
        if lst_job:
            hr_position_history = self.env['hr.position.history']
            for employee in lst_job.keys():
                today = fields.Date.context_today(self)
                hr_position_history.create({
                    'employee_id': employee.id,
                    'date': today,
                    'old_position_id': lst_job[employee] and
                    lst_job[employee].id or False,
                    'new_position_id': employee.job_id and
                    employee.job_id.id or False,
                })
        return res
