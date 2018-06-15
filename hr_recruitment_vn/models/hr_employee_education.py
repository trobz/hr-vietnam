# Copyright 2009-2018 Trobz (http://trobz.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HrEmployeeEducation(models.Model):
    _inherit = 'hr.employee.education'

    applicant_id = fields.Many2one('hr.applicant', 'Applicant')
