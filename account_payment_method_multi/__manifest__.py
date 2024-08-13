# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Cybernetics+ - Account Payment Method Multi',
    'version': '17.0',
    'category': 'Account',
    'description': """

Account Payment Method Multi
===============================
Account Payment Method

    """,
    'author': 'Cybernetics+',
    'website': 'http://www.cybernetics.plus/',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'account',
        'account_payment',
        'account_wht',
        'account_cheque',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',
        'views/account_payment_line_view.xml',
        'views/account_move_view.xml',
    ],
}
