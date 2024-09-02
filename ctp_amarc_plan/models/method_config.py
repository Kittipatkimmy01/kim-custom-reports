from odoo import models, fields


class MethodConfig(models.Model):
    _name = 'method.config'

    name = fields.Char(string='Name')
