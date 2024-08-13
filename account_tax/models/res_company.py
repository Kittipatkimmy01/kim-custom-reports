# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    account_purchase_vat_report_id = fields.Many2one(
        'account.account',
        string='Purchase Vat Report Account',
        required=False,
        ondelete="cascade",
    )
    account_sale_vat_report_id = fields.Many2one(
        'account.account',
        string='Sale Vat Report Account',
        required=False,
        ondelete="cascade",
    )
