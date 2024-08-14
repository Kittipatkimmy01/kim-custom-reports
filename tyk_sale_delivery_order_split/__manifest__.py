# -*- coding: utf-8 -*-
{
    'name': 'C+ | Tyk | Delivery Order Split',
    'summary': """This module allows you to split the sale delivery order according to the product's availability """,
    'description': """This module allows you to split the sale delivery order according to the product's availability in the warehouse""",
    "author": "Cybernetics+",
    'category': 'Sales',
    'version': '0.1',
    'website': 'https://www.cybernetics.plus',
    'license': 'LGPL-3',
    'depends': [
        'sale_stock',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/stock_views.xml',
        'wizard/sale_delivery_order_split_wizard.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}