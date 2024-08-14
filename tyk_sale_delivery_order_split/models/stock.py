# -*- coding: utf-8 -*-
import datetime
from odoo import models, api, fields
from odoo.exceptions import ValidationError


class StockPickingExtended(models.Model):
    _inherit = "stock.picking"

    split_from_id = fields.Many2one(
        comodel_name='stock.picking',
        readonly=True,
        string='Split From'
    )

    def prepare_delivery_items(self, move):
        return {
            'picking_id': move.picking_id.id,
            'name': move.description_picking,
            'product_id': move.product_id.id,
            'quantity': move.product_uom_qty,
            'location_id': move.location_id.id,
            'location_dest_id': move.location_dest_id.id,
            'stock_move_id': move.id,
        }

    def split_sale_delivery_order(self):
        for rec in self:
            delivery_items = []

            for move_id in rec.move_ids_without_package:
                delivery_items += [(0, 0, self.prepare_delivery_items(move_id))]

            res_id = (
                self.env['sale.delivery.order.split.wizard'].create(
                    {'picking_id': self.id, 'transfer_item_detail_ids': delivery_items})).id

            return {
                'name': 'Split Order',
                'type': 'ir.actions.act_window',
                'res_model': 'sale.delivery.order.split.wizard',
                'view_type': 'form',
                'view_mode': 'form',
                'res_id': res_id,
                'target': 'new',
            }
