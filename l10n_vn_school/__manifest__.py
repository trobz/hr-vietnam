# -*- coding: utf-8 -*-
# Copyright 2016 Trobz
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Vietnam School List",
    "summary": "Vietnam School List",
    "version": "10.0.1.0.0",
    "category": "localization",
    "website": "https://trobz.com",
    "author": "Trobz, "
              "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "base",
        "hr",
    ],
    "data": [
        # view
        'views/school_category_view.xml',
        'views/school_school_view.xml',
        'views/school_menu.xml',

        # security
        'security/ir.model.access.csv',

        # data
        "data/school_category.xml",
        "data/school_school.xml",
    ],
    'installable': True,
}
