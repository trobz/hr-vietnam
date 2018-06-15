# -*- coding: utf-8 -*-
# Copyright 2009-2018 Trobz (http://trobz.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class HrSalaryAdjustment(models.Model):
    _name = 'hr.salary.adjustment'
    _order = 'date desc, id desc'

    name = fields.Text(
        string='Description', required=True,
        states={'paid': [('readonly', True)]}
    )
    employee_id = fields.Many2one(
        comodel_name='hr.employee', string='Employee', required=True,
        states={'paid': [('readonly', True)]}
    )
    contract_id = fields.Many2one(
        comodel_name='hr.contract', string='Contract',
        states={'paid': [('readonly', True)]},
    )
    date = fields.Date(
        string='Apply Date', required=True,
        states={'paid': [('readonly', True)]}
    )
    rule_id = fields.Many2one(
        comodel_name='hr.salary.rule', string="Salary Rule", required=True,
        states={'paid': [('readonly', True)]},
        domain=[('is_adjust', '=', True)]
    )
    amount = fields.Float(
        string="Amount", required=True, states={'paid': [('readonly', True)]})
    state = fields.Selection([
        ('new', "New"),
        ('paid', "Paid"),
    ], string="State", readonly=True, default='new',
        help="This record will be changed to `paid` automatically"
        " when approving payslip"
    )
    payslip_id = fields.Many2one(
        comodel_name='hr.payslip', string="Payslip", readonly=True
    )

    @api.depends('rule_id')
    def _compute_required_contract(self):
        """
        Local rule: required contract
        Global rule: Not require contract
        """
        for record in self:
            if not record.rule_id.is_unique_on_payslip:
                record.required_contract = True
            else:
                record.required_contract = False

    required_contract = fields.Boolean(compute=_compute_required_contract)

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        """
        Only calculate contract when select a local rule
        """
        if not self.employee_id or self.rule_id.is_unique_on_payslip:
            # no employee and global rule, do nothing
            return
        today = fields.Date.today()
        contract_ids = self.env['hr.payslip'].get_contract(
            self.employee_id, self.date, today)
        self.contract_id = contract_ids and contract_ids[0] or False

    @api.multi
    def unlink(self):
        """
        state = paid, not allow to edit
        """
        for record in self:
            if record.state == 'paid':
                raise ValidationError(_("You cannot delete paid records."))
        return super(HrSalaryAdjustment, self).unlink()
