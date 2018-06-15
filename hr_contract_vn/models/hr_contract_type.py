# -*- coding: utf-8 -*-
# Copyright 2009-2018 Trobz (http://trobz.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, fields


class HrContractType(models.Model):
    _inherit = 'hr.contract.type'

    count_working_seniority = fields.Boolean(
        string='Working Seniority',
        help="The contracts which activate this field will be taken into "
        "account the calculation of working seniority", default=False)

    allowance_ids = fields.One2many(
        'hr.contract.allowance',
        'contract_type_id',
        'Allowance Template')
