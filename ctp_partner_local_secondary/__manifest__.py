# -*- coding: utf-8 -*-
###################################################################################
#
#    Cybernetics Plus Co., Ltd.
#    Address Secondary Language 
#
#    Copyright (C) 2021-TODAY Cybernetics Plus Technologies (<https://www.cybernetics.plus>).
#    Author: Cybernetics Plus Techno Solutions (<https://www.cybernetics.plus>)
#
###################################################################################

{
    "name": "Address Secondary Language",
    "version": "17.0.1.0.1",
    "summary": "Address Secondary Language",
    "description": "Address Secondary Language",
    "author": "Cybernetics+",
    "website": "https://www.cybernetics.plus",
    "live_test_url": "https://www.cybernetics.plus",
    "images": ["static/description/banner.png"],
    "category": "Customizations",
    "license": "AGPL-3",
    "price": 9999999999.99,
    "currency": "EUR",
    "application": False,
    "installable": True,
    "auto_install": False,
    "contributors": [
        "C+ Developer <dev@cybernetics.plus>",
    ],
    "depends": ["base_setup"],
    "data": [
        'data/res_config.xml',
        "views/report_invoice.xml",
        "views/res_config_settings_view.xml",
        "views/res_company_view.xml",
        "views/sale_order.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "/ctp_partner_local_secondary/static/src/scss/partner_local_secondary.scss",
        ],
    },
}