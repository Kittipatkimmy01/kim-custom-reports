# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    is_internal_voucher = fields.Boolean(
        string='Internal Voucher',
        default=False,
    )

