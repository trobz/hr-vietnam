# -*- coding: utf-8 -*-
# Copyright 2009-2018 Trobz (http://trobz.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import time

from odoo import api, models, fields, _
from odoo.exceptions import Warning,ValidationError

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def _default_date_from(self):
        """
        Advanced payslip: get current date
        """
        if self._context.get('default_is_advance'):
            return time.strftime('%Y-%m-%d')
        return time.strftime('%Y-%m-01')

    is_advance = fields.Boolean('Is Advanced?', default=False)
    advance_amount = fields.Float(
        string='Amount', readonly=True, default=0,
        states={'draft': [('readonly', False)]}, required=True)
    date_from = fields.Date(
        default=_default_date_from,
        string='Date From', readonly=True,
        states={'draft': [('readonly', False)]}, required=True)
    date_to = fields.Date(
        string='Date To', readonly=True,
        states={'draft': [('readonly', False)]}, required=True)

    @api.one
    @api.constrains('advance_amount')
    def _check_amount(self):
        if self.is_advance and self.advance_amount <= 0:
            raise ValidationError(
                _('Advanced Amount must be greater than 0.'))

    @api.multi
    def check_done(self):
        """
        Check if exist a advance payslip: NOT done the payslips automatically
        """
        for payslip in self:
            if payslip.is_advance:
                return False
        return True

    @api.onchange('is_advance', 'date_from', 'date_to', 'employee_id')
    def onchange_employee(self):
        """
        Override function, for advanced payslip:
            Payslip name: Advance slip of Employee_name For Month-Year
            Date to = Date from
            Structure = Advanced Salary
        """
        res = super(HrPayslip, self).onchange_employee()
        if not self.is_advance:
            return res
        # Set date_to = date from for advanced payslip
        self.date_to = self.date_from
        self.struct_id = self.env.ref(
            'hr_payroll_advance_vn.hr_payroll_structure_advanced_salary').id

    @api.multi
    def hr_verify_sheet(self):
        self.compute_sheet()
        return self.write({'state': 'verify'})

    @api.multi
    def compute_sheet(self):
        """
            Override Function
            Add is_advance in context to prevent the updating of
                the computed_on_payslip_days on holiday lines
        """
        advance_ids_count = self.search_count(
            [('id', 'in', self._ids), ('is_advance', '=', True)]
        )
        if advance_ids_count and advance_ids_count != len(self._ids):
            raise Warning(
                _('You cannot approve monthly payslips and advanced payslips '
                  'at same time! Please approve the advanced payslips first.'))
        return super(HrPayslip, self).compute_sheet()
