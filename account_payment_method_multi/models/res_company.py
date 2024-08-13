# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    non_reconcile = fields.Boolean(
        string='Non Reconcile',
        readonly=False,
    )
