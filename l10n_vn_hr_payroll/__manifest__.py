# -*- coding: utf-8 -*-
# Copyright 2009-2018 Trobz (http://trobz.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': 'Vietnam Salary Structure',
    'version': '11.0.1.0.1',
    "author": "Trobz, Odoo Community Association (OCA)",
    "website": "http://trobz.com",
    'license': 'AGPL-3',
    'category': 'Human Resources',
    'depends': [
        'hr_employee_vn',
        'hr_payroll_advance_vn',
    ],
    'data': [
        # data
        'data/hr_salary_rule_category_data.xml',
        'data/hr_salary_rule_data.xml',
        'data/hr_payroll_structure_data.xml',

        # view
        'views/hr_payslip_view.xml',

    ],
    'installable': True,
    'application': True,
}
