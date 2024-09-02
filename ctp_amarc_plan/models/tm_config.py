from odoo import models, fields


class TMConfig(models.Model):
    _name = 'tm.config'

    name = fields.Char(string='Name')
