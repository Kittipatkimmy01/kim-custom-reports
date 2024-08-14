# -*- coding: utf-8 -*-
{
    'name': 'C+ | Tyk | Second UOM',
    "author": "Cybernetics+",
    'category': 'Sales',
    'website': 'https://www.cybernetics.plus',
    'license': 'LGPL-3',
    'version': '0.1',
    'depends': [
        'product',
        'purchase_stock',
        'sale_stock',
        'tyk_sale_delivery_order_split',
    ],
    'data': [
        'views/product_views.xml',
        'views/sale_views.xml',
        'views/purchase_views.xml',
        'views/account_move_views.xml',
        'views/stock_move_views.xml',
        'wizard/sale_delivery_order_split_wizard.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}