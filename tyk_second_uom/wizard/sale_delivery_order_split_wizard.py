from odoo import api, fields, models, _


class SplitDelivery(models.TransientModel):
    _inherit = "sale.delivery.order.split.wizard"

    def _prepare_split_one(self, line, move):
        res = super()._prepare_split_one(line, move)
        res['second_uom_id'] = line.second_uom_id.id
        res['qty_second_uom'] = line.qty_second_uom
        res['is_active_2nd_uom'] = line.is_active_2nd_uom
        return res

    def _prepare_split_two(self, line, move):
        res = super()._prepare_split_two(line, move)
        res['second_uom_id'] = move.second_uom_id.id
        res['qty_second_uom'] = move.qty_second_uom - line.qty_second_uom
        res['is_active_2nd_uom'] = line.is_active_2nd_uom
        return res

    def _prepare_split_two_not_match_move(self, line):
        res = super()._prepare_split_two_not_match_move(line)
        res['second_uom_id'] = line.second_uom_id.id
        res['qty_second_uom'] = line.qty_second_uom
        res['is_active_2nd_uom'] = line.is_active_2nd_uom
        return res
