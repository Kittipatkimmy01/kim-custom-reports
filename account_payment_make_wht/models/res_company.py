# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class ResCompany(models.Model):
    _inherit = 'res.company'


    payment_method3_id = fields.Many2one(
        'account.payment.method.multi',
        ondelete="cascade",
        string='Payment WHT PND3',
        required = False,
    )
    payment_method53_id = fields.Many2one(
        'account.payment.method.multi',
        ondelete="cascade",
        string='Payment WHT PND53',
        required = False,
    )
    payment_method54_id = fields.Many2one(
        'account.payment.method.multi',
        ondelete="cascade",
        string='Payment WHT PND54',
        required = False,
    )
    sale_method3_id = fields.Many2one(
        'account.payment.method.multi',
        ondelete="cascade",
        string='Sale WHT PND3',
        required=False,
    )
    sale_method53_id = fields.Many2one(
        'account.payment.method.multi',
        ondelete="cascade",
        string='Sale WHT PND53',
        required=False,
    )
    partner_wht_id = fields.Many2one(
        string='Partner WHT',
        comodel_name='res.partner',
    )
    acc_pnd54_ext_id = fields.Many2one(
        comodel_name='account.account',
        string='PND54(EXP)',
        required=False,
    )
    acc_pnd54_ap_id = fields.Many2one(
        comodel_name='account.account',
        string='PND54(AP)',
        required=False,
    )
