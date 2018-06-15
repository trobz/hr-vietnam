# -*- coding: utf-8 -*-
# Copyright 2009-2018 Trobz (http://trobz.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class EthnicGroup(models.Model):
    _name = 'ethnic.group'

    name = fields.Char("Name", required=True)
    is_default = fields.Boolean("Is Default?")
