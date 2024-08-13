# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class Partner(models.Model):
    _inherit = 'res.partner'

    branch = fields.Char(
        string='Branch.',
    )
