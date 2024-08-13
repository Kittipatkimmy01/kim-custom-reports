{
    'name': 'CTP Base Customs Reports',
    'version': '17.0.1.0.1',
    'category': 'Tools',
    'depends': ['base', 'account', 'sale', 'purchase'],
    'license': 'OPL-1',
    'author': 'Cybernetics+',
    'website': 'https://www.cybernetics.plus',
    "live_test_url": "https://www.cybernetics.plus",
    'description': """
        Custom Base Reports
    """,
    'data': [
        'views/res_company_view.xml',
        'views/res_partner_view.xml',
        'views/sale_order_view.xml',
        'views/purchase_order_view.xml',
        'views/hr_employee_view.xml',
        'views/layouts.xml',
        'reports/sale_report_document.xml',
        'reports/purchase_report_document.xml',
        'reports/billing_report_document.xml',
        'reports/copy_payment_report_document.xml',
        'reports/original_tax_inv_report_document.xml',
        'reports/copy_rv_tax_inv_report_document.xml',
        'reports/copy_tax_inv_report_document.xml',
        'reports/original_invoice_report_document.xml',
        'reports/original_payment_report_document.xml',
        'reports/original_rv_tax_inv_report_document.xml',
        'reports/report_picking_slip.xml',
    ],
}