from odoo import api, fields, models, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    je_type = fields.Selection(selection=[('general', 'General'), ('receive', 'Receive'), ('pay', 'Pay')],
                               string="Type")
    voucher_running_no = fields.Char(string="Voucher No.")
    trade_discount = fields.Float(string='Trade Discount', store=True)
    trade_discount_type = fields.Selection([
        ('percent', '%'),
        ('amount', 'Amount'),
    ], string='Discount Type', default='percent')
    amount_untaxed_before_trade_discount = fields.Float(string='Untaxed Amount before Trade Discount', store=True,
                                                        compute="_compute_amount_trade",
                                                        readonly=True, digits='Discount')
    amount_trade_discount = fields.Monetary(string='Trade Discount Amount', store=True, compute="_compute_amount_trade",
                                            readonly=True)


    @api.depends('invoice_line_ids.price_total')
    def _compute_amount_trade(self):
        for invoice in self:
            amount_trade_discount = sum(
                invoice.invoice_line_ids.filtered(lambda line: line.is_trade_discount).mapped('price_subtotal'))
            invoice.update({
                'amount_untaxed_before_trade_discount': invoice.amount_untaxed - amount_trade_discount,
                'amount_trade_discount': -amount_trade_discount,
                'amount_tax': invoice.amount_tax,
            })


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    product_uom_id = fields.Many2one('uom.uom', string="UoM")
    is_trade_discount = fields.Boolean('Is Trade Discount?', default=False)
    discount_type = fields.Selection([
        ('percent', '%'),
        ('amount', 'Amount'),
        ('amount_per_unit', 'Amount (per unit)'),
    ], string='Discount Type', default='percent')
