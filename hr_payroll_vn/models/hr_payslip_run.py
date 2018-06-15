# -*- coding: utf-8 -*-
# Copyright 2009-2018 Trobz (http://trobz.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'
    _order = 'date_end desc, id desc'
