# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    account_purchase_vat_report_id = fields.Many2one(
        'account.account',
        string='Purchase Vat Report Account',
        readonly=False,
        required=False,
        ondelete="cascade",
        related='company_id.account_purchase_vat_report_id',
    )
    account_sale_vat_report_id = fields.Many2one(
        'account.account',
        string='Sale Vat Report Account',
        readonly=False,
        required=False,
        ondelete="cascade",
        related='company_id.account_sale_vat_report_id',
    )
