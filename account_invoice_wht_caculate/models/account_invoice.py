# -*- coding: utf-8 -*-

from odoo import fields, models, api, _

class AccountMove(models.Model):
    _inherit ='account.move'

    def _compute_amount_wth(self):
        for invoice in self:
            amount_wht = sum(line.total_wht for line in invoice.invoice_line_ids)
            invoice.amount_after_wht = invoice.amount_total - amount_wht
            invoice.amount_wht = round(amount_wht, 2)

    amount_wht = fields.Monetary(
        string = 'Amount WHT',
        compute = '_compute_amount_wth',
    )
    amount_after_wht = fields.Monetary(
        string = 'Amount Payment',
        compute = '_compute_amount_wth',
    )


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    _order = "credit asc, account_id asc"

    @api.depends('wht_type', 'price_subtotal')
    def _compute_total_wht(self):
        for line in self:
            if line.wht_type and line.price_subtotal:
                line.total_wht = round(line.price_subtotal * ((line.wht_type.percentage or 1) / 100), 2)
            else:
                line.total_wht = 0

    wht_type = fields.Many2one(
        'account.wht.type',
        string='WHT',
        store=True,
    )
    total_wht = fields.Float(
        string='Total WHT',
        compute='_compute_total_wht',
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'product_id' in vals:
                pp = self.env['product.product'].browse(vals['product_id'])
                if pp.wht_type:
                    vals['wht_type'] = pp.wht_type.id
        lines = super().create(vals_list)
        return lines

    @api.onchange('product_id')
    def _onchange_prod_wht(self):
        """docstring for _onchange_prod_wht"""
        for rec in self:
            prod = rec.product_id
            if prod.wht_type:
                rec.wht_type = prod.wht_type

    def write(self, vals):
        """docstring for write"""
        res = super(AccountMoveLine, self).write(vals)
        return res

