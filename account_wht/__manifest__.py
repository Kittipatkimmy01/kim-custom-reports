# -*- coding: utf-8 -*-


{
    "name" : "Standard Accounting - WHT",
    "version" : "17.0",
    "depends" : [
        "account",
        "account_accountant",
        "ctp_thai_reading_words"
    ],
    "author" : "C+",
    "category": "Accounting",
#     "external_dependencies": {"python": ["fillpdf"]},
    "description": """
    * WHT thai tax
    - apt-get install jython //java -jar jython_installer-2.5.2.jar[(/usr/local/lib/jython)sudo ln -s /usr/local/lib/jython/bin/jython /usr/bin/jython]
    - cp module_account_v10/account_base_functional/account_wht/report/itextpdf-5.4.1.jar  /usr/share/java/.
    """,
    "website": "https://cybernetics.plus",
    "data": [
        "security/ir.model.access.csv",
        "data/wht_data.xml",
        "data/ir_rules.xml",
        "data/paper_format.xml",
        "data/withholding_tax_cert_data.xml",
        "wizard/data_template_pnd3.xml",
#         "views/account_payment_mode_view.xml",
        "views/wht_view.xml",
        # "views/sale_order.xml",
        "reports/withholding_tax_cert_form_view.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "/account_wht/static/src/scss/thai_tax_report.scss",
            "/account_wht/static/src/scss/thai_tax_state.scss",
        ],
        "web.report_assets_common":[
            "/account_wht/static/src/scss/thai_tax_style_report.scss",
        ],
    },
    "demo": [],
    "license": "LGPL-3",
    "installable": True,
    "auto_install": False,
    "images": ["images/icon.png"],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
