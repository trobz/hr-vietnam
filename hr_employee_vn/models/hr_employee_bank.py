# -*- coding: utf-8 -*-
# Copyright 2009-2018 Trobz (http://trobz.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class HrEmployeeBank(models.Model):
    _name = 'hr.employee.bank'

    bank_account_id = fields.Many2one(
        'res.partner.bank',
        'Bank Account Number',
        required=True)
    payroll_account = fields.Boolean('Payroll account', default=False)
    employee_id = fields.Many2one('hr.employee', 'Employee', required=True)

    @api.one
    @api.constrains('payroll_account', 'employee_id', 'bank_account_id')
    def _check_unique_payroll_account(self):
        if self.employee_id and self.payroll_account:
            exist_bank_account = self.search([
                ('employee_id', '=', self.employee_id.id),
                ('payroll_account', '=', True),
                ('id', '!=', self.id)
            ])
            if exist_bank_account:
                raise ValidationError(
                    _('One employee only have one payroll account!'))
        if self.bank_account_id and self.employee_id:
            exist_bank_account = self.search(
                [('employee_id', '=', self.employee_id.id),
                    ('bank_account_id', '=', self.bank_account_id.id),
                 ('id', '!=', self.id)])
            if exist_bank_account:
                raise ValidationError(
                    _('Duplicate bank account!'))
        return True
