# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class AccountPaymentMethod(models.Model):
    _name = 'account.payment.method.multi'
    _description = "Account Payment Method"

    name = fields.Char(
        'Payment Name',
        required=True,
    )
    type = fields.Selection(
        [('cash','Cash'),
         ('cheque','Cheque'),
         ('bank','Bank'),
         ('discount','Discount'),
         ('wht', 'WHT'),
         ('ap','AP'),
         ('ar','AR'),
         ('advance_receipt', 'Advance Receipt'),
         ('other','Other')],
        'Payment method',
        required=True
    )
    account_id = fields.Many2one(
        'account.account',
        string="Account",
        required=True
    )
    parent_id = fields.Many2one(
        'account.payment.method.multi',
        string="Parent"
    )
    percent = fields.Float(
        'Percent',
        default=100.0,
        digits=(3,3),
        required=True
    )
    put_select_account = fields.Selection(
        selection=[
            ('debit', 'Debit'),
            ('credit', 'Credit'),
        ],
        string='Put Select Account',
    )


