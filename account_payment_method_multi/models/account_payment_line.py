# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError

class AccountPaymentLine(models.Model):
    _name ='account.payment.line'
    _description = 'Payment Line'

    payment_id =fields.Many2one(
        'account.payment',
        string='Payment',
        ondelete = 'restrict',
    )
    payment_method_id = fields.Many2one(
        'account.payment.method.multi',
        string='Method',
        required=True
    )
    bank_id = fields.Many2one(
        'res.bank',
        string="Bank"
    )
#     cheque_number = fields.Char(
#         'Cheque Number'
#     )
#     cheque_date = fields.Date(
#         'Cheque Date'
#     )
#     cheque_id = fields.Many2one(
#         'tr.cheque',
#         string='Cheque',
#         readonly=False,
#         domain="[('state', '=','draft')]",
#     )
    wht_id = fields.Many2one(
        'account.wht',
        string='WHT',
        readonly=False,
        domain="[('state', '=','draft')]",
    )
    paid_total = fields.Float(
        string='Total',
        required=True,
    )

    payment_method_line_type = fields.Selection(
        related='payment_method_id.type',
    )

    def create_cheque(self):
        if self.paid_total <= 0:
            raise ValidationError(_('Total Payment Method Not Less more Zero.'))
        if self.cheque_id:
            raise ValidationError(_('You have cheque alredy!'))
        if not self.bank_id:
            raise ValidationError(_('No Bank! Please insert bank'))

        if not self.cheque_number:
            raise ValidationError(_('No Cheque number! Please insert Cheque number'))
        if not self.cheque_date:
            raise ValidationError(_('No Date! Please insert date'))
        if self.payment_id.payment_type == 'inbound':
            cheque_type = 'in'
            if not self.bank_id.cheque_income_account_id:
                raise ValidationError(_('No Bank Account! Please insert Account for Bank'))
            bank_id = self.bank_id.cheque_income_account_id.id

        else:
            cheque_type = 'out'
            if not self.bank_id.cheque_out_account_id:
                raise ValidationError(_('No Bank Account! Please insert Account for Bank'))
            bank_id = self.bank_id.cheque_out_account_id.id

        cheque_vals = {
                'name': self.cheque_number,
                'cheque_date': self.cheque_date,
                'bank':self.bank_id.id,
                'partner_id': self.payment_id and self.payment_id.partner_id.id or self.payment_id.partner_id.id,
                'journal_id': self.payment_id and self.payment_id.journal_id.id or self.payment_id.journal_id.id,
                'amount': self.paid_total,
                'type': cheque_type,
                'date_receipt':self.payment_id and self.payment_id.payment_date,
                'account_receipt_id': bank_id,
                'account_pay_id': bank_id,
                'payment_id' :self.payment_id.id,
                'payment_method_id': self.payment_method_id.id,
            }
        self.cheque_id= self.env['tr.cheque'].create(cheque_vals)
