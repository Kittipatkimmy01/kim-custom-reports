# -*- coding: utf-8 -*-

from odoo import fields, models, api, _

class AccountPaymentLine(models.Model):
    _name =  'account.invoice.payment.line'
    _description = 'Invoice Payment Line'

    payment_id = fields.Many2one(
        'account.payment',
    )
    invoice_id = fields.Many2one(
        'account.move',
        string = "Invoice",
    )
    dute_date = fields.Date(
        string = 'Due Date',
    )
    amount = fields.Float(
        string = 'Amount',
    )
    balance = fields.Float(
        string = 'Balance',
    )
    wht_total = fields.Float(
        string = 'WHT',
    )
    paid_amount = fields.Float(
        string = 'Paid',
    )
    currency_id = fields.Many2one(
        'res.currency',
        string="Currency",
    )

    @api.onchange('invoice_id')
    def onchange_invoice(self):
        invoice = self.invoice_id
        self.dute_date = invoice.invoice_date_due
        self.amount = invoice.amount_total
        self.balance = invoice.amount_residual
        self.wht_total =  invoice.amount_wht
        self.currency_id = invoice.currency_id

    @api.onchange('paid_amount')
    def onchage_paid_amount(self):
        if self.paid_amount > self.balance:
            raise ValidationError(_('Error!\nThe paid amount over balance.'))

    def check_full(self):
        self.paid_amount = self.balance
        self.payment_id.update({'amount': self.payment_id.amount})
