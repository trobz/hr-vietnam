# -*- coding: utf-8 -*-
# Copyright 2009-2018 Trobz (http://trobz.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SchoolCategory(models.Model):
    _name = 'school.category'

    name = fields.Char("Name", required=True)
    code = fields.Char("Code")
