# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    "name": "Cybernetics+ - Account Payment Make WHT",
    "version": "1.0",
    "category": "Account",
    "description": """

Account Payment Make WHT
===============================
Account Payment Make WHT

    """,
    "author": "Cybernetics+",
    "website": "http://www.cybernetics.plus/",
        "depends": [
            "base",
            "account",
            "account_wht",
            "account_payment_method",
            "account_payment_method_multi",
        ],
    "data": [
        "security/ir.model.access.csv",
        "wizard/wizard_payment_make_wht_view.xml",
        "wizard/wizard_clear_pnd54_view.xml",
        "views/account_config.xml",
        "views/account_payment_view.xml",
    ],
    "license": "OEEL-1",
}
