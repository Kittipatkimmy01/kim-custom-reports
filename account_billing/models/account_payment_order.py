# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class AccountPaymentOrder(models.Model):
    _inherit = 'account.payment.order'

    billing_id = fields.Many2one(
        comodel_name='account.billing',
        string='Billing',
    )

    @api.onchange('billing_id')
    def onchange_billing(self):
        """docstring for onchange_billing"""
        for rec in self:
            if rec.billing_id:
                rec.partner_id = rec.billing_id.partner_id.id

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        """docstring for onchange"""
        line_list = []
        if self.partner_id:
            AM = self.env['account.move']
            domain = [
                ('partner_id', '=', self.partner_id.id),
                ('state', '=', 'posted'),
            ]
            if self.payment_type == 'outbound':
                domain.append(('move_type', 'in', ('in_invoice', 'in_refund')))
            else:
                domain.append(('move_type', 'in', ('out_invoice', 'out_refund')))
            move_search = AM.search(domain)
            move_bill_ids = []
            if self.billing_id:
                for bline in self.billing_id.line_ids:
                    move_bill_ids.append(bline.move_id.id)
            for move in move_search:
                if move_bill_ids and move.id not in move_bill_ids:
                    continue
                applicable_lines = move.line_ids.filtered(
                    lambda x: (
                        not x.reconciled
                        and x.account_id.account_type in ("asset_receivable", "liability_payable")
                        and not any(
                            p_state in ("draft", "open", "generated")
                            for p_state in x.payment_line_ids.mapped("state")
                        )
                    )
                )
                if not applicable_lines:
                    continue
                payment_type = self.payment_type
                for line in applicable_lines:
                    vals_line = line._prepare_payment_line_onchange_vals(payment_type)
                    vals_line['communication_type'] = 'normal'
                    vals_line['communication'] = move.name
                    line_list.append((0, 0,vals_line))
        self.payment_line_ids = line_list
