# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    payment_count = fields.Integer(
        string='Payment Count',
        compute='_compute_payment_count',
    )

    def _compute_payment_count(self):
        """docstring for _compute_payment_count"""
        for rec in self:
            payment_count = 0
            ivl = self.env['account.invoice.payment.line'].search([('invoice_id', '=', rec.id)])
            if ivl:
                payment_count = len(ivl.mapped('payment_id'))
            rec.payment_count = payment_count

    def action_view_payment(self):
        ivl = self.env['account.invoice.payment.line'].search([('invoice_id', '=', self.id)])
        moves = ivl.mapped('payment_id')
        action = self.sudo().env.ref('account.action_account_payments').read()[0]
        if len(moves) > 1:
            action['domain'] = [('id', 'in', moves.ids)]
        elif len(moves) == 1:
            action['views'] = [(self.env.ref('account.view_account_payment_form').id, 'form')]
            action['res_id'] = moves.id
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action
