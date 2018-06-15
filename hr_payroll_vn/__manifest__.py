# -*- coding: utf-8 -*-
# Copyright 2009-2018 Trobz (http://trobz.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Vietnam HR Payroll",
    'version': '11.0.1.0.1',
    "author": "Trobz, Odoo Community Association (OCA)",
    "website": "http://trobz.com",
    'license': 'AGPL-3',
    'category': 'Human Resources',
    "depends": [
        # OpenERP Modules
        'hr_payroll_account',
        # Trobz Standard
        'hr_contract_vn',
        # 'hr_holidays_extension',
    ],
    'init_xml': [],
    'data': [
        # data
        'data/ir_config_parameter_data.xml',

        # views
        'views/hr_holidays_status_view.xml',
        'views/hr_salary_rule_view.xml',
        'views/hr_payroll_structure_view.xml',
        'views/hr_payslip_view.xml',
        'views/hr_salary_adjustment_view.xml',
        'views/hr_menu.xml',
        'wizard/salary_adjustment_path_view.xml',

        # security
        "security/ir.model.access.csv",
    ],
    'installable': True,
}
