# -*- coding: utf-8 -*-
{
    "name": "Account Billing Notes",
"version": "17.0.1.0.1",
    "category": "Accounting",
    "license": "LGPL-3",
    # "external_dependencies": {"python": ["bahttext"]},
    "depends": ["account",
                # "tyk_base_reports", 
                # "account_payment_order"
                ],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        # "report/billing_report.xml",
        "views/account_billing_views.xml",
        "views/account_move_views.xml",
        "views/sequence_views.xml",
        # "views/account_payment_order.xml",
    ],
    "installable": True,
    "auto_install": False,
    "application": False,
}
