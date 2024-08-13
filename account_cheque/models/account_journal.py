# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    is_cheque = fields.Boolean(
        string='Is Cheque',
        default=False,
    )
    cheque_income_account_id = fields.Many2one(
        comodel_name="account.account",
        string="Cheque Income Account",
        required=False,
    )
    cheque_out_account_id = fields.Many2one(
        comodel_name="account.account",
        string="Cheque Out Account",
        required=False,
    )
