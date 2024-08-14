# -*- coding: utf-8 -*-
from odoo import api, fields, models


class TransferItemDetail(models.TransientModel):
    _inherit = "sale.transfer.item.detail"

    second_uom_id = fields.Many2one('uom.uom', string="2nd UoM")
    qty_second_uom = fields.Float(digits='Product Unit of Measure', string='2nd Quantity')
    is_active_2nd_uom = fields.Boolean(string='Active 2nd UoM',default=True,)
