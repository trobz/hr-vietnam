# Copyright 2009-2018 Trobz (http://trobz.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class HrApplicant(models.Model):
    _inherit = 'hr.applicant'

    def _get_ethnic_group(self):
        ethnic_group = self.env['ethnic.group'].search([
            ('is_default', '=', True)])
        return ethnic_group and ethnic_group.ids[0] or False

    identification_id = fields.Char('Identification No')
    id_date_issue = fields.Date(
        string='ID Date Of Issue',
        help='Date of issue of identity document')
    id_place_issue_id = fields.Many2one(
        'res.country.state',
        string='ID Place Of Issue',
        help='Place of issue of identity document')
    passport_id = fields.Char('Passport No')
    ethnic_group_id = fields.Many2one(
        'ethnic.group', 'Ethnic Group', default=_get_ethnic_group)
    religion = fields.Char('Religion')
    education_ids = fields.One2many(
        'hr.employee.education', 'applicant_id', 'Education')
    work_permit_expire_date = fields.Date('Work Permit Expire Date')

    @api.multi
    def create_employee_from_applicant(self):
        """ Override to update more fields when create employee"""
        res = super(HrApplicant, self).create_employee_from_applicant()
        employee = self.env['hr.employee'].browse(res['res_id'])
        if employee:
            for applicant in self:
                employee.update({
                    'identification_id': applicant.identification_id or '',
                    'id_date_issue': applicant.id_date_issue or False,
                    'id_place_issue_id': applicant.id_place_issue_id and
                    applicant.id_place_issue_id.id or False,
                    'passport_id': applicant.passport_id or '',
                    'ethnic_group_id': applicant.ethnic_group_id and
                    applicant.ethnic_group_id.id or False,
                    'religion': applicant.religion or '',
                    'education_ids': [(6, 0, applicant.education_ids and
                                       applicant.education_ids.ids or [])],
                    'work_permit_expire_date':
                    applicant.work_permit_expire_date or False
                })
        return res
