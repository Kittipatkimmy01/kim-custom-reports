from odoo import models, fields


class ResCompany(models.Model):
    _inherit = "res.company"

    fax = fields.Char("Fax")