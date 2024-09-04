# -*- coding: utf-8 -*-
###################################################################################
#
#    Cybernetics Plus Co., Ltd.
#    Print PDF Options
#
#    Copyright (C) 2021-TODAY Cybernetics Plus Technologies (<https://www.cybernetics.plus>).
#    Author: Cybernetics Plus Techno Solutions (<https://www.cybernetics.plus>)
#
###################################################################################

{
    "name": "Print PDF Options",
    "version": "17.0.1.0.1",
    "summary": """ 
        Choose one of the following options when printing a pdf report:
        - print. print the pdf report directly with the browser
        - download. download the pdf report on your computer
        - open. open the pdf report in a new tab
        You can also set a default options for each report
            """,
    "description": """ 
        Choose one of the following options when printing a pdf report:
        - print. print the pdf report directly with the browser
        - download. download the pdf report on your computer
        - open. open the pdf report in a new tab
        You can also set a default options for each report
            """,
    "author": "Cybernetics+",
    "website": "https://www.cybernetics.plus",
    "live_test_url": "https://www.cybernetics.plus",
    "category": "Tools",
    "license": "LGPL-3",
    "installable": True,
    "application": False,
    "auto_install": False,
    "contributors": [
        "C+ Developer <dev@cybernetics.plus>",
    ],
    "depends": ["web"],
    "data": [
        "views/ir_actions_report.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "/ctp_print_options/static/src/**/*.js",
            "/ctp_print_options/static/src/**/*.xml",
        ]
    }
}