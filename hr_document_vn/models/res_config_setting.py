# -*- coding: utf-8 -*-
# Copyright 2009-2018 Trobz (http://trobz.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    reminder_doc_expiring_in_30_days = fields.Boolean(
        string="Send weekly reminder to HR Manager "
        "for Documents expiring in 30 days",
        implied_group='hr.group_hr_manager'
    )
    reminder_doc_expired = fields.Boolean(
        string='Send weekly reminder to HR Manager for Documents expired',
        implied_group='hr.group_hr_manager'
    )

    def get_values(self):
        """
        Read document configurations from system parameter
        """
        res = super(ResConfigSettings, self).get_values()
        param_obj = self.env['ir.config_parameter']
        reminder_doc_expiring_in_30_days = param_obj.get_param(
            'reminder_doc_expiring_in_30_days', 'False'
        )
        reminder_doc_expired = param_obj.get_param(
            'reminder_doc_expired', 'False'
        )
        res.update({
            'reminder_doc_expiring_in_30_days':
                eval(reminder_doc_expiring_in_30_days),
            'reminder_doc_expired': eval(reminder_doc_expired),
        })
        return res

    def set_values(self):
        """
        Update changing configurations to system parameter
        """
        super(ResConfigSettings, self).set_values()
        param_obj = self.env['ir.config_parameter']
        for record in self:
            param_obj.sudo().set_param(
                'reminder_doc_expiring_in_30_days',
                record.reminder_doc_expiring_in_30_days or 'False'
            )
            param_obj.sudo().set_param(
                'reminder_doc_expired',
                record.reminder_doc_expired or 'False'
            )
