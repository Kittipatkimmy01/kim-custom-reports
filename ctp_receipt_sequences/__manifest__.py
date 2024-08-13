# -*- coding: utf-8 -*-
###################################################################################
#
#    Cybernetics Plus Co., Ltd.
#    Add Field Receipt Sequences
#
#    Copyright (C) 2021-TODAY Cybernetics Plus Technologies (<https://www.cybernetics.plus>).
#    Author: Cybernetics Plus Techno Solutions (<https://www.cybernetics.plus>)
#
###################################################################################

{
    "name": "Receipt Sequences",
    "version": "17.0.1.0.1",
    "summary": "Add Field Receipt Sequences",
    "description": "Add Field Receipt Sequences",
    "author": "Cybernetics+",
    "website": "https://www.cybernetics.plus",
    "live_test_url": "https://www.cybernetics.plus",
    "images": ["static/description/icon.png"],
    "category": "CTP",
    "license": "AGPL-3",
    "price": 999999.00,
    "currency": "USD",
    "application": False,
    "auto_install": False,
    "installable": True,
    'autostart': True,
    "contributors": [
        "C+ Developer <dev@cybernetics.plus>",
    ],
    "depends": [
        "account_accountant",
    ],
    "data": [
        "data/seq_receipt_sequences.xml",
        "views/account_move.xml",
    ],
}