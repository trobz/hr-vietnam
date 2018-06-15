# -*- coding: utf-8 -*-
# Copyright 2009-2018 Trobz (http://trobz.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class HrContract(models.Model):
    _inherit = 'hr.contract'

    @api.multi
    def _compute_contract_time(self):
        """
        @return past/current/future by compare today with the contract duration
        """
        today = datetime.now().strftime("%Y-%m-%d")
        contracts = self.env['hr.contract'].search([])
        for contract in contracts:
            if contract.date_end and contract.date_end < today:
                contract.contract_time = 'past'
            elif (contract.date_end and contract.date_end > today) or \
                    (not contract.date_end and
                     contract.date_start < today):
                contract.contract_time = 'current'
            elif contract.date_start > today:
                contract.contract_time = 'future'

    contract_time = fields.Selection(
        [('past', 'Past'), ('current', 'Current'), ('future', 'Future')],
        string="Contract Time", compute=_compute_contract_time
    )
    department_id = fields.Many2one(
        'hr.department', string='Department',
        related='employee_id.department_id', store=True,
        depends=('employee_id', 'employee_id.department_id')
    )
    allowance_ids = fields.One2many(
        'hr.contract.allowance',
        'contract_id',
        'Allowance')

    @api.onchange('type_id')
    def _onchange_type_id(self):
        if self.type_id and self.type_id.allowance_ids:
            for allowance in self.type_id.allowance_ids:
                new_allowance = self.allowance_ids.new({
                    'rule_id': allowance.rule_id and allowance.rule_id or False,
                    'code': allowance.code,
                    'description': allowance.description,
                    'amount': allowance.amount,
                    'apply_on': allowance.apply_on,
                })
                self.allowance_ids |= new_allowance

    @api.constrains('date_start', 'date_end', 'employee_id')
    def _check_date(self):
        for record in self:
            employee_id = record.employee_id.id
            # previous contracts without date end
            contracts_no_date_end = self.search(
                [('date_start', '<=', record.date_start),
                 ('date_end', '=', False),
                 ('employee_id', '=', employee_id),
                 ('id', '!=', record.id)])
            if contracts_no_date_end:
                raise Warning(
                    _("The previous contract (ID: %s, %s) must be ended "
                      "before creating a new contract." %
                      (contracts_no_date_end[0].id,
                       contracts_no_date_end[0].name))
                )
            elif record.date_end:
                contracts = self.search(
                    [('date_start', '<=', record.date_end),
                     ('date_end', '>=', record.date_start),
                     ('employee_id', '=', employee_id),
                     ('id', '!=', record.id)])
            elif not record.date_end:
                contracts = self.search(
                    [('date_end', '>=', record.date_start),
                     ('employee_id', '=', employee_id),
                     ('id', '!=', record.id)])
            if contracts:
                raise ValidationError(
                    _("You cannot have 2 contracts of an employee "
                      "overlapped on the same duration."))

    @api.multi
    def unlink(self):
        not_draft_contract = self.filtered(lambda obj: obj.state != 'draft')
        if not_draft_contract:
            raise ValidationError(_("You only can delete draft contract!"))
        try:
            return super(HrContract, self).unlink()
        except BaseException:
            raise ValidationError(_("This contract is being used. You "
                                    "cannnot delete it."))
