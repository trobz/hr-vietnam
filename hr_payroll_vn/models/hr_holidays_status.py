# -*- coding: utf-8 -*-
# Copyright 2009-2018 Trobz (http://trobz.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, fields


class HrHolidaysStatus(models.Model):
    _inherit = "hr.holidays.status"

    code = fields.Char(string='Code', size=16)
    payment_type = fields.Selection([('paid', 'Paid'),
                                     ('unpaid', 'Unpaid')],
                                    string='Payment Type',
                                    default="paid")
