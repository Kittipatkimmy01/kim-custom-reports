# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class StockPicking(models.Model):
	_inherit = 'stock.picking'

	def prepare_delivery_items(self, move):
		res = super().prepare_delivery_items(move)
		res['second_uom_id'] = move.second_uom_id.id
		res['qty_second_uom'] = move.qty_second_uom
		res['is_active_2nd_uom'] = move.is_active_2nd_uom
		return res


class StockMove(models.Model):
	_inherit = 'stock.move'

	second_uom_id = fields.Many2one('uom.uom', string="2nd UoM")
	qty_second_uom = fields.Float(digits='Product Unit of Measure', string='2nd Demand')
	is_active_2nd_uom = fields.Boolean(string='Active 2nd UoM',default=True,)


class StockMoveLine(models.Model):
	_inherit = 'stock.move.line'

	second_uom_id = fields.Many2one('uom.uom', string="2nd UoM")
	qty_second_uom = fields.Float(digits='Product Unit of Measure', string='2nd Demand')
	is_active_2nd_uom = fields.Boolean(string='Active 2nd UoM',default=True,)
