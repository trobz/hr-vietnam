# -*- coding: utf-8 -*-
# Copyright 2009-2018 Trobz (http://trobz.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class HrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'
    _order = 'sequence'

    is_unique_on_payslip = fields.Boolean('Global Rule', default=False)
    is_adjust = fields.Boolean('Can be adjusted', default=False)

    @api.model
    def _recursive_search_of_rules_unique(self, rule_ids):
        """
        Copy function _recursive_search_of_rules,
        add is_unique_on_payslip in return values
        @param rule_ids: list of browse record
        @return: returns a list of tuple (id, sequence)
            which are all the children of the passed rule_ids
        """
        children_rules = []
        for rule in rule_ids:
            if rule.child_ids:
                children_rules += self._recursive_search_of_rules_unique(
                    rule.child_ids)
        return [(r.id, r.sequence, r.is_unique_on_payslip)
                for r in rule_ids] + children_rules
