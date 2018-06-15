# -*- coding: utf-8 -*-
# Copyright 2009-2018 Trobz (http://trobz.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Vietnam HR contract",
    'version': '11.0.1.0.1',
    "author": "Trobz, Odoo Community Association (OCA)",
    "website": "http://trobz.com",
    'license': 'AGPL-3',
    'category': 'Human Resources',
    "depends": [
        "hr_contract",
        "hr_payroll",
    ],
    'data': [
        # data
        'views/hr_contract_type_view.xml',
        'views/hr_contract_view.xml',

        # view

        # security
        'security/ir.model.access.csv',
    ],
    'installable': True,
}
