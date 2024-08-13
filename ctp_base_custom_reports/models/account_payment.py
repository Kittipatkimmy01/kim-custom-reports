from odoo import models, fields, api, _


class AccountPayment(models.Model):
    _inherit = "account.payment"

    amount_net = fields.Float("Net Received")
    amount_fee = fields.Float("Net Fee")
    amount_wht = fields.Float("Withholding Tax")
    exchange_rate = fields.Float("Exchange Rate", digits=(12, 6))
    inv_untaxed = fields.Float("Untaxed Invoice", compute='_compute_inv_untaxed')
    inv_tax = fields.Float("Tax Invoice", compute='_compute_inv_untaxed')
    inv_total = fields.Float("Total Invoice", compute='_compute_inv_untaxed')
    inv_residual = fields.Float("Residual Invoice", compute='_compute_inv_untaxed')
    account_payment_method_id = fields.Many2one('account.payment.method', string='Payment Method')
