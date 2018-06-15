# Copyright 2009-2018 Trobz (http://trobz.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Vietnam Working Hour Management',
    'version': '11.0.1.0.0',
    'category': 'Human Resources',
    'license': 'AGPL-3',
    'author': 'Trobz, Odoo Community Association (OCA)',
    'website': 'https://www.trobz.com',
    'depends': [
        'l10n_vn_hr_payroll',
        'hr_working_hour',
    ],
    'data': [
        # data
        'data/hr_salary_rule_data.xml',
        # views

        # security
    ],
    'installable': True,
}
