# -*- coding: utf-8 -*-
# Copyright 2009-2018 Trobz (http://trobz.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class SalaryAdjustmentPath(models.TransientModel):
    _name = 'salary.adjustment.path'
    _description = 'Salary Adjustment Path'

    name = fields.Text(
        string='Description', required=True
    )
    employee_ids = fields.Many2many(
        'hr.employee', 'employee_salary_adjustment_rel',
        'adj_id', 'emp_id', string='Employees')
    date = fields.Date(
        string='Apply Date', required=True
    )
    rule_id = fields.Many2one(
        comodel_name='hr.salary.rule', string="Salary Rule", required=True,
        domain=[('is_adjust', '=', True)]
    )
    amount = fields.Float(
        string="Amount", required=True
    )

    @api.multi
    def action_import(self):
        salary_adjustment = self.env['hr.salary.adjustment']
        payslip = self.env['hr.payslip']
        salary_adjustment_ids = []
        for obj in self:
            for employee in obj.employee_ids:
                contract_ids = payslip.get_contract(
                    employee, obj.date, obj.date)
                if not contract_ids:
                    raise ValidationError(
                        _('Dont have contract of %s on %s' % (employee.name, obj.date)))
                new_adj = salary_adjustment.create({
                    'name': obj.name,
                    'employee_id': employee.id,
                    'contract_id': contract_ids[0],
                    'date': obj.date,
                    'rule_id': obj.rule_id.id,
                    'amount': obj.amount,
                })
                salary_adjustment_ids += [new_adj.id]
        return {
            'name': _('Salary Adjustment'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'hr.salary.adjustment',
            'domain': [('id', 'in', salary_adjustment_ids)],
        }
