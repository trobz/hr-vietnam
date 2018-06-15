# -*- coding: utf-8 -*-
# Copyright 2009-2018 Trobz (http://trobz.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': 'Vietnam HR Employee',
    'version': '11.0.1.0.1',
    "author": "Trobz, Odoo Community Association (OCA)",
    "website": "http://trobz.com",
    'license': 'AGPL-3',
    'category': 'Human Resources',
    'depends': [
        'hr',
        'l10n_vn_country_state',
        'l10n_vn_school',
    ],
    'data': [
        # data
        'data/employee_data.xml',

        # view
        'views/ethnic_group_view.xml',
        'views/hr_employee_relation_view.xml',
        'views/hr_job_level_view.xml',
        'views/hr_employee_view.xml',

        # security
        'security/ir.model.access.csv',
    ],
    'installable': True,
}
