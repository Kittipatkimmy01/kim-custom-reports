# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    "name": "Account Payment Method",
    "version": "1.0",
    "category": "Account",
    "description": """

Account Payment Method
===============================
Account Payment Method

    """,
    "author": "",
    "website": "",
    "depends": ["account"],
    "license": "LGPL-3",
    "data": [
        "security/ir.model.access.csv",
        "views/payment_method_view.xml",
    ],
}
