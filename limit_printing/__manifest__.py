{
    "name": "Limit Printing",
    "version": "17.0.1.0.1",
    "category": "Tools",
    "depends": ["base", "web", "ctp_print_options", "approvals", "sale", "purchase"],
    "license": "OPL-1",
    "author": "Cybernetics+",
    "website": "https://www.cybernetics.plus",
    "live_test_url": "https://www.cybernetics.plus",
    "description": """ """,
    "data": [
        "data/data.xml",
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/actions_report.xml",
        "views/ir_actions_report.xml",
        "views/log_reports.xml",
        "views/approve.xml",
        "views/sale_order.xml",
        "views/purchase_order.xml",
        "views/status_for_print.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "limit_printing/static/src/**/*.xml",
            "limit_printing/static/src/**/*.js",
        ]
    },
}
