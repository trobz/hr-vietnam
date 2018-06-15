# -*- coding: utf-8 -*-
# Copyright 2009-2018 Trobz (http://trobz.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class HrEmployeeEducation(models.Model):
    _name = 'hr.employee.education'

    level = fields.Char('Level')
    school_id = fields.Many2one('school.school', 'School')
    degree = fields.Char('Degree')
    major = fields.Char('Major', required=True)
    graduated_year = fields.Char('Graduated year', size=4)
    main_qualification = fields.Boolean('Main qualification')
    employee_id = fields.Many2one('hr.employee', 'Employee')

    @api.constrains('graduated_year')
    def _check_graduated_year(self):
        if self.graduated_year and not self.graduated_year.isdigit() or \
                int(self.graduated_year) < 0:
            raise UserError(
                _('Graduated year must be an integer and greater than zero'))
        return True
