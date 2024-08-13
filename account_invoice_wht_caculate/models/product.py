# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class ProductTemplate(models.Model):
    _inherit ='product.template'

    wht_type = fields.Many2one(
        'account.wht.type',
        string = 'WHT TYPE',
    )
