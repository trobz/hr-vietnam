# -*- coding: utf-8 -*-
# Copyright 2009-2018 Trobz (http://trobz.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class HrPayrollStructure(models.Model):
    _inherit = 'hr.payroll.structure'

    active = fields.Boolean(
        'Active', default=True, help="If the active field is set to False, "
        "it will allow you to hide the structure without removing it.")

    @api.model
    def get_all_rules_unique(self):
        """
        Copy function get_all_rules, call _recursive_search_of_rules_unique
        @param structure_ids: list of structure
        @return: returns a list of tuple (id, sequence)
        """
        all_rules = []
        rule_obj = self.env['hr.salary.rule']
        for struct in self:
            all_rules += \
                rule_obj._recursive_search_of_rules_unique(struct.rule_ids)
        return all_rules
