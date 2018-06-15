# Copyright 2009-2018 Trobz (http://trobz.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Vietnam HR Recruitment',
    'summary': 'This module extends the feature applicant management',
    'version': '11.0.1.0.1',
    "author": "Trobz, Odoo Community Association (OCA)",
    "website": "http://trobz.com",
    'license': 'AGPL-3',
    'category': 'Human Resources',
    'depends': [
        'hr_recruitment',
        'hr_employee_vn',
    ],
    'data': [
        # view
        'views/hr_applicant_view.xml',
    ],
    'installable': True,
}
