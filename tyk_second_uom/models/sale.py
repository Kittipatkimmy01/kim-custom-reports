# -*- coding: utf-8 -*-
from odoo import models, api, fields


class SaleOrder(models.Model):
    _inherit = "sale.order"

    partner_id = fields.Many2one(
        domain="[('customer_rank', '>', 0), ('type', '!=', 'private'), ('company_id', 'in', (False, company_id)), ('parent_id', '=', False)]"
    )

    def action_confirm(self):
        res = super().action_confirm()
        for rec in self:
            for line in rec.order_line:
                rec.picking_ids.filtered(
                    lambda x: x.state in ['confirmed', 'assigned']
                ).move_ids_without_package.filtered(
                    lambda x: x.sale_line_id.id == line.id
                ).write({
                    'second_uom_id': line.second_uom_id.id,
                    'qty_second_uom': line.qty_second_uom,
                    'is_active_2nd_uom': line.is_active_2nd_uom,
                })
        return res


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    second_uom_id = fields.Many2one('uom.uom', string="2nd UoM")
    qty_second_uom = fields.Float(digits='Product Unit of Measure', string='2nd Quantity')
    is_active_2nd_uom = fields.Boolean(string='Active 2nd UoM', default=True,)

    @api.model
    def create(self, vals):
        if 'product_uom_qty' in vals and vals.get('product_uom_qty'):
            vals['qty_second_uom'] = vals['product_uom_qty']
        if 'product_uom' in vals and vals.get('product_uom'):
            vals['second_uom_id'] = vals['product_uom']
        return super(SaleOrderLine, self).create(vals)

    def write(self, vals):
        if 'product_uom_qty' in vals:
            vals['qty_second_uom'] = vals['product_uom_qty']
        if 'product_uom' in vals:
            vals['second_uom_id'] = vals['product_uom']
        res = super(SaleOrderLine, self).write(vals)
        return res

    @api.onchange('product_id')
    def _onchange_set_2nd_uom(self):
        self.update({'second_uom_id': self.product_id.second_uom_id.id})

    def _prepare_invoice_line(self, **optional_values):
        res = super(SaleOrderLine, self)._prepare_invoice_line(**optional_values)
        if res:
            res.update({
                'second_uom_id': self.second_uom_id.id,
                'qty_second_uom': self.qty_second_uom,
                'is_active_2nd_uom': self.is_active_2nd_uom,
            })
        return res
