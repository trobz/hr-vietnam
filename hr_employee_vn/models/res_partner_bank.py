# -*- coding: utf-8 -*-
# Copyright 2009-2018 Trobz (http://trobz.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    @api.one
    @api.constrains('acc_number', 'bank_id')
    def _check_unique_account_number(self):
        if self.acc_number:
            exist_bank_account = self.search([
                ('acc_number', '=', self.acc_number),
                ('bank_id', '=', self.bank_id and self.bank_id.id or False),
                ('id', '!=', self.id)
            ])
            if exist_bank_account:
                raise ValidationError(
                    _('Bank account must be unique!'))
        return True
