# -*- coding: utf-8 -*-
# Copyright 2009-2018 Trobz (http://trobz.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': 'Vietnam HR Documents',
    'version': '11.0.1.0.1',
    "author": "Trobz, Odoo Community Association (OCA)",
    "website": "http://trobz.com",
    'license': 'AGPL-3',
    'category': 'Human Resources',
    'depends': [
        'hr',
    ],
    'data': [
        # data
        'data/hr_document_type_data.xml',
        'data/mail_template_data.xml',
        'data/ir_config_parameter_data.xml',
        'data/ir_cron_data.xml',

        # view
        'views/res_config_setting_view.xml',
        'views/hr_document_type_view.xml',
        'views/hr_document_view.xml',
        'views/hr_employee_view.xml',

        # menu
        'views/hr_menu.xml',

        # security
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
    ],
    'installable': True,
}
