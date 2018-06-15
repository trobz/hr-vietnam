# Copyright 2009-2018 Trobz (http://trobz.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models, api


class SchoolSchool(models.Model):
    _name = 'school.school'

    name = fields.Char("Name", required=True)
    code = fields.Char("Code")
    description = fields.Char("Description")
    categ_id = fields.Many2one('school.category', 'Category')

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|','|',('code','ilike',name),
                      ('name','ilike',name),('description','ilike',name)]
        shools = self.search(domain + args, limit=limit)
        return shools.name_get()