import datetime
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SplitDelivery(models.TransientModel):
    _name = "sale.delivery.order.split.wizard"

    picking_id = fields.Many2one("stock.picking", string='Transfer')
    transfer_item_detail_ids = fields.One2many(
        'sale.transfer.item.detail',
        'delivery_order_id',
        string='Delivery Orders'
    )
    scheduled_date = fields.Datetime(string='Scheduled Date', default=fields.Datetime.now)

    def _prepare_split_one(self, line, move):
        return {
            'product_id': line.product_id.id,
            'product_uom_qty': line.quantity,
            'name': line.product_id.name_get()[0][1],
            'date': self.scheduled_date,
            'date_deadline': self.scheduled_date,
            'product_uom': line.product_id.uom_po_id.id,
            'location_id': line.location_id.id,
            'location_dest_id': line.location_dest_id.id,
            'group_id': move.group_id.id,
            'sale_line_id': move.sale_line_id.id,
        }

    def _prepare_split_two(self, line, move):
        return {
            'product_id': line.product_id.id,
            'product_uom_qty': move.product_uom_qty - line.quantity,
            'name': line.product_id.name_get()[0][1],
            'date': move.date,
            'date_deadline': move.date_deadline,
            'product_uom': line.product_id.uom_po_id.id,
            'location_id': line.location_id.id,
            'location_dest_id': line.location_dest_id.id,
            'group_id': move.group_id.id,
            'sale_line_id': move.sale_line_id.id,
        }

    def _prepare_split_two_not_match_move(self, line):
        return {
            'product_id': line.product_id.id,
            'product_uom_qty': line.product_uom_qty,
            'name': line.name,
            'date': line.date,
            'date_deadline': line.date_deadline,
            'product_uom': line.product_id.uom_po_id.id,
            'location_id': line.location_id.id,
            'location_dest_id': line.location_dest_id.id,
            'group_id': line.group_id.id,
            'sale_line_id': line.sale_line_id.id,
        }

    def split_sale_transfer(self):

        split_one = []
        split_two = []
        changes = []

        for move_id in self.picking_id.move_ids_without_package:
            equivalent_line = self.transfer_item_detail_ids.filtered(
                lambda item_line: item_line.stock_move_id.id == move_id.id)
            if equivalent_line:
                if equivalent_line.quantity < move_id.product_uom_qty:
                    changes.append(True)
                else:
                    changes.append(False)
            else:
                changes.append(True)

        if not any(changes) or not self.transfer_item_detail_ids:
            raise ValidationError('Orders with no modification is not allowed.')

        else:

            move_ids_without_package = self.picking_id.move_ids_without_package
            for line in self.transfer_item_detail_ids:
                move_id = line.stock_move_id
                qty_one = line.quantity
                qty_two = move_id.product_uom_qty - line.quantity

                if qty_one > 0.0:
                    split_one += [(0, 0, self._prepare_split_one(line, move_id))]
                if qty_two > 0.0:
                    split_two += [(0, 0, self._prepare_split_two(line, move_id))]

                match_move = self.picking_id.move_ids_without_package.filtered(lambda x: x == line.stock_move_id)
                if match_move:
                    move_ids_without_package -= match_move

                move_id.sale_line_id = False

            for line in move_ids_without_package:
                split_two += [(0, 0, self._prepare_split_two_not_match_move(line))]

            self.picking_id.do_unreserve()
            self.picking_id.write({'state': 'draft'})
            self.picking_id.move_ids_without_package.write({'state': 'draft'})
            if split_one:
                print('BBBBBBBBBB', split_one)
                new_order_id = self.env['stock.picking'].create({
                    'scheduled_date': self.scheduled_date,
                    'partner_id': self.transfer_item_detail_ids[0].picking_id.partner_id.id,
                    'location_id': self.transfer_item_detail_ids[0].picking_id.location_id.id,
                    'location_dest_id': self.transfer_item_detail_ids[0].picking_id.location_dest_id.id,
                    'picking_type_id': self.transfer_item_detail_ids[0].picking_id.picking_type_id.id,
                    'split_from_id': self.transfer_item_detail_ids[0].picking_id.id,
                    'origin': self.transfer_item_detail_ids[0].picking_id.origin,
                    'move_ids_without_package': split_one,
                    'sale_id': self.picking_id.sale_id and self.picking_id.sale_id.id
                })
            self.picking_id.move_ids_without_package = False
            self.picking_id.write({'move_ids_without_package': split_two})
            self.picking_id.action_confirm()
            new_order_id.action_confirm()
            action = self.sudo().env.ref('stock.action_picking_tree_all').read()[0]
            action['domain'] = [('id', 'in', (new_order_id + self.picking_id).ids)]
            return action
