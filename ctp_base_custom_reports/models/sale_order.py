from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    order_type = fields.Selection(string='Order Type', selection=[('normal', 'Normal'), ('project', 'Project'),
                                                                  ('cliam', 'Cliam')])
    exchange_rate = fields.Float(string='Exchange Rate')
    department_id = fields.Many2one('hr.department', string='Department')
    transport_address = fields.Char(string='Transportation Address')
