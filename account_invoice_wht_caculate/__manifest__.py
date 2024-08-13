# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    "name": "Cybernetics+ - Account Invoice WHT Caculate",
    "version": "17.0",
    "category": "Account",
    "description": """

Account Invoice WHT Caculate
===============================
Invoice WHT Caculate


    """,
    "author": "Cybernetics+",
    "website": "http://www.cybernetics.plus/",
    "depends": ["account","account_wht"],
    "license": "LGPL-3",
    "data": [
        "views/account_invoice_view.xml",
        "views/product_view.xml",
    ],
}
