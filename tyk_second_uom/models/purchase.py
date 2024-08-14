# -*- coding: utf-8 -*-
from odoo import models, api, fields


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    second_uom_id = fields.Many2one('uom.uom', string="2nd UoM")
    qty_second_uom = fields.Float(digits='Product Unit of Measure', string='2nd Quantity')
    is_active_2nd_uom = fields.Boolean(string='Active 2nd UoM',default=True,)

    @api.onchange('product_id')
    def _onchange_set_2nd_uom(self):
        if self.product_id and self.product_id.second_uom_po_id:
            self.update({'second_uom_id': self.product_id.second_uom_po_id.id})

    def _prepare_stock_move_vals(self, picking, price_unit, product_uom_qty, product_uom):
        res = super(PurchaseOrderLine, self)._prepare_stock_move_vals(picking, price_unit, product_uom_qty, product_uom)
        res['second_uom_id'] = self.second_uom_id.id
        res['qty_second_uom'] = self.qty_second_uom
        res['is_active_2nd_uom'] = self.is_active_2nd_uom
        return res

    def _prepare_account_move_line(self, move=False):
        res = super()._prepare_account_move_line(move)
        res['second_uom_id'] = self.second_uom_id.id
        res['qty_second_uom'] = self.qty_second_uom
        res['is_active_2nd_uom'] = self.is_active_2nd_uom
        if self.product_id:
            res['name'] = self.product_id.name
        return res

class Purchase(models.Model):
    _inherit = 'purchase.order'

    partner_id = fields.Many2one(
        domain="[('supplier_rank', '>', 0),'|', ('company_id', '=', False), ('company_id', '=', company_id)]"
    )
