# -*- coding: utf-8 -*-
from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    billing_count = fields.Integer(
        compute='_compute_billing_count',
    )

    def _compute_billing_count(self):
        for rec in self:
            rec.billing_count = self.env['account.billing.line'].search_count([
                ('move_id', '=', rec.id)
            ])

    def open_billing_view(self):
        billing_ids = self.env['account.billing.line'].search([
            ('move_id', '=', self.id)
        ]).mapped('billing_id')
        action = self.env.ref('account_billing.account_billing_action').read()[0]
        action['domain'] = [('id', 'in', billing_ids.ids)]
        return action
