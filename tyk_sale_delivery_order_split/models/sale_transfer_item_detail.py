# -*- coding: utf-8 -*-
from odoo import api, fields, models


class TransferItemDetail(models.TransientModel):
    _name = "sale.transfer.item.detail"

    picking_id = fields.Many2one('stock.picking')
    stock_move_id = fields.Many2one('stock.move')
    stock_move_line_id = fields.Many2one('stock.move.line')
    product_id = fields.Many2one('product.product', string='Product')
    name = fields.Char(
        string='Description',
    )
    quantity = fields.Float(string='Quantity')
    location_id = fields.Many2one('stock.location', string='Source Location')
    location_dest_id = fields.Many2one('stock.location', string='Destination Location')
    delivery_order_id = fields.Many2one('sale.delivery.order.split.wizard')
