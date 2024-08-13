# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class AccountPaymentMode(models.Model):
    _inherit = 'account.payment.mode'

    is_wht = fields.Boolean(
        string='Is WHT Mode',
    )
