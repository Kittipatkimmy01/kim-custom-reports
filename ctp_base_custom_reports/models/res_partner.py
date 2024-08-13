from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    fax = fields.Char("Fax")