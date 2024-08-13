# -*- coding: utf-8 -*-
###################################################################################
#
#    Cybernetics Plus Co., Ltd.
#    Thai Accounting Install Module
#
#    Copyright (C) 2021-TODAY Cybernetics Plus Technologies (<https://www.cybernetics.plus>).
#    Author: Cybernetics Plus Techno Solutions (<https://www.cybernetics.plus>)
#
###################################################################################

{
    "name": "Account Install Module",
    "version": "17.0",
    "summary": """ 
            Thai Accounting Install Module
            .""",
    "description": """ 
            Thai Accounting Install Module
            .""",
    "author": "Cybernetics+",
    "website": "https://www.cybernetics.plus",
    "live_test_url": "https://www.cybernetics.plus",
    "category": "Report",
    "license": "AGPL-3",
    "price": 0,
    "currency": "THB",
    "application": True,
    "installable": True,
    "auto_install": True,
    "contributors": [
        "C+ Developer <dev@cybernetics.plus>",
    ],
    "depends": [
        "base",
        "account",
        "account_accountant",
        "account_wht",
        "ctp_thai_reading_words",
        "account_invoice_wht_caculate",
        "account_payment_method",
        "account_cheque",
        "account_payment_method_multi",
        "account_payment_make_wht",
        "account_tax",
    ],
    "data": [
    ],
}
