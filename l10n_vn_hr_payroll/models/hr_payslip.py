# -*- coding: utf-8 -*-
# Copyright 2009-2018 Trobz (http://trobz.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    thirdteenth_year = fields.Char('Year of 13th Month Salary', readonly=True,
        states={'draft': [('readonly', False)]})

    @api.constrains('thirdteenth_year')
    def _check_thirdteenth_year(self):
        for payslip in self:
            if not payslip.thirdteenth_year:
                continue
            try:
                thirdteenth_year = int(payslip.thirdteenth_year)
                if thirdteenth_year < 2000:
                    raise Warning(
                        _('Year of 13th month salary must be greater than '
                          '2000!'))
            except Exception:
                raise Warning(
                    _('Please check year format. It must be a number ('
                      'Ex: 2018).'))

        return True
