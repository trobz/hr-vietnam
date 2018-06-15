# -*- coding: utf-8 -*-
# Copyright 2009-2018 Trobz (http://trobz.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, fields


class HrPayslipLine(models.Model):
    _inherit = 'hr.payslip.line'

    contract_id = fields.Many2one(required=False)
