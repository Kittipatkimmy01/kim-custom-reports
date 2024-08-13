# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo import SUPERUSER_ID

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    payment_method3_id = fields.Many2one(
        'account.payment.method.multi',
        ondelete="cascade",
        string='Payment WHT PND3',
        required = False,
        readonly=False,
        related='company_id.payment_method3_id',
    )
    payment_method53_id = fields.Many2one(
        'account.payment.method.multi',
        ondelete="cascade",
        string='Payment WHT PND53',
        required = False,
        readonly=False,
        related='company_id.payment_method53_id',
    )
    payment_method54_id = fields.Many2one(
        'account.payment.method.multi',
        ondelete="cascade",
        string='Payment WHT PND54',
        required = False,
        readonly=False,
        related='company_id.payment_method54_id',
    )
    sale_method3_id = fields.Many2one(
        'account.payment.method.multi',
        ondelete="cascade",
        string='Sale WHT PND3',
        required=False,
        readonly=False,
        related='company_id.sale_method3_id',
    )
    sale_method53_id = fields.Many2one(
        'account.payment.method.multi',
        ondelete="cascade",
        string='Sale WHT PND53',
        required=False,
        readonly=False,
        related='company_id.sale_method53_id',
    )
    partner_wht_id = fields.Many2one(
        string='Partner WHT',
        comodel_name='res.partner',
        related='company_id.partner_wht_id',
        readonly=False,
    )
    acc_pnd54_ext_id = fields.Many2one(
        comodel_name='account.account',
        string='PND54(EXP)',
        required=False,
        readonly=False,
        related='company_id.acc_pnd54_ext_id',
    )
    acc_pnd54_ap_id = fields.Many2one(
        comodel_name='account.account',
        string='PND54(AP)',
        required=False,
        readonly=False,
        related='company_id.acc_pnd54_ap_id',
    )


