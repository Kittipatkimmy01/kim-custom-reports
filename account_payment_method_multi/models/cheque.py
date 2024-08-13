# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class account_cheque(models.Model):
    _inherit = 'account.cheque'

    payment_id = fields.Many2one(
        comodel_name='account.payment',
        string='Payment',
    )

