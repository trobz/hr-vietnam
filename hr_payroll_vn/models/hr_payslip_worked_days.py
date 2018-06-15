# -*- coding: utf-8 -*-
# Copyright 2009-2018 Trobz (http://trobz.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class HrPayslipWorkedDays(models.Model):
    _inherit = 'hr.payslip.worked_days'
    _order = 'payslip_id, contract_id, sequence ASC'
