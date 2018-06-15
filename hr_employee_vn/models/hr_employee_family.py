# -*- coding: utf-8 -*-
# Copyright 2009-2018 Trobz (http://trobz.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HrEmployeeFamily(models.Model):
    _name = 'hr.employee.family'

    relation_id = fields.Many2one(
        'hr.employee.relation',
        'Relation',
        required=True)
    name = fields.Char('Name', required=True)
    birthday = fields.Date('Birthday')
    identification = fields.Char('Identification/ Passport No')
    tin = fields.Char('TIN')
    mobile = fields.Char('Mobile')
    description = fields.Char('Description')
    address = fields.Char('Address')
    dependent = fields.Boolean('Dependent')
    employee_id = fields.Many2one(
        'hr.employee',
        'Employee',
        required=True,
        ondelete='cascade')
