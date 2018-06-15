# -*- coding: utf-8 -*-
# Copyright 2009-2018 Trobz (http://trobz.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class HrContractAllowance(models.Model):
    _name = 'hr.contract.allowance'

    rule_id = fields.Many2one(
        'hr.salary.rule',
        'Rule',
        domain=[('is_unique_on_payslip', '=', False)])
    code = fields.Char('Code', required=True)
    description = fields.Text('Description')
    amount = fields.Float('Amount')
    apply_on = fields.Selection(
        [('monthly', 'Monthly'), ('daily', 'Daily'), ('hourly', 'Hourly')],
        string='Apply on', default='monthly')
    contract_id = fields.Many2one('hr.contract', 'Contract')
    contract_type_id = fields.Many2one('hr.contract.type', 'Contract Type')

    @api.onchange('rule_id')
    def onchange_rule_id(self):
        if self.rule_id:
            if self.contract_id and self.contract_id.struct_id and \
                    self.rule_id.id not in self.contract_id.struct_id.rule_ids.ids:
                raise ValidationError(
                    _("Please select rule in salary structure on contract."))
            self.code = self.rule_id.code
            self.description = self.rule_id.name

    @api.constrains('rule_id')
    def _check_rule_id(self):
        for record in self:
            if record.rule_id and record.contract_id \
                    and record.contract_id.struct_id and \
                    record.rule_id.id not in record.contract_id.struct_id.rule_ids.ids:
                raise ValidationError(_(
                    "Please select rule in salary structure on contract."))
