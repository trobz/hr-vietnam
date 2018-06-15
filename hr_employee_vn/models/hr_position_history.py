# -*- coding: utf-8 -*-
# Copyright 2009-2018 Trobz (http://trobz.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HrPositionHistory(models.Model):
    _name = 'hr.position.history'

    old_position_id = fields.Many2one('hr.job', 'Old Position')
    new_position_id = fields.Many2one('hr.job', 'New Position', required=True)
    date = fields.Date('Date', required=True)
    employee_id = fields.Many2one('hr.employee', 'Employee', required=True)
