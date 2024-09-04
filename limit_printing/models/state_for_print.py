from odoo import models, fields


class StateForPrint(models.Model):
    _name = 'state.for.print'

    name = fields.Char()
    color = fields.Integer(string='Color')
