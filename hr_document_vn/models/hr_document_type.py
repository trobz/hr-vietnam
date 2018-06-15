# -*- coding: utf-8 -*-
# Copyright 2009-2018 Trobz (http://trobz.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HrDocumentType(models.Model):

    _name = "hr.document.type"

    name = fields.Char(string='Name', required=True, translate=True)
    mandatory_issue_date = fields.Boolean(string='Mandatory Issue Date')
    mandatory_expiry_date = fields.Boolean(string='Mandatory Expiry Date')
    mandatory_issue_place = fields.Boolean(string='Mandatory Issue Place')
    mandatory_issue_by = fields.Boolean(string='Mandatory Issue By')
    required = fields.Boolean('Required')
