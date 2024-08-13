# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    non_reconcile = fields.Boolean(
        string='Non Reconcile',
        related='company_id.non_reconcile',
        readonly=False,
    )
