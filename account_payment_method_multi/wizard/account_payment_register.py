# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    def _create_payment_vals_from_wizard(self, batch_result):
        payment_vals = super()._create_payment_vals_from_wizard(batch_result)
        val = []
        line = self.line_ids
        moves = line.mapped('move_id')
        paid_amount = self.amount
        for move in moves:
#             if move.amount_residual < self.amount:
#                 paid_amount = move.amount_residual
            val.append((0, 0, {
                'invoice_id': move.id,
                'dute_date' : move.invoice_date_due,
                'amount' : move.currency_id._convert(move.amount_total, self.company_id.currency_id, self.company_id, self.payment_date),
                'wht_total': move.currency_id._convert(move.amount_wht, self.company_id.currency_id, self.company_id, self.payment_date),
                'balance' : move.currency_id._convert(move.amount_residual, self.company_id.currency_id, self.company_id, self.payment_date),
                'currency_id' : self.currency_id.id,
                'paid_amount': move.currency_id._convert(paid_amount, self.company_id.currency_id, self.company_id, self.payment_date),
            }))
        payment_vals['invoice_line'] = val
        return payment_vals

    def _create_payment_vals_from_batch(self, batch_result):
        payment_vals = super()._create_payment_vals_from_batch(batch_result)
        val = []
        line = batch_result['lines']
        moves = line.mapped('move_id')
        paid_amount = self.amount
        for move in moves:
#             if move.amount_residual < self.amount:
#                 paid_amount = move.amount_residual
            val.append((0, 0, {
                'invoice_id': move.id,
                'dute_date' : move.invoice_date_due,
                'amount' : move.currency_id._convert(move.amount_total, self.company_id.currency_id, self.company_id, self.payment_date),
                'wht_total': move.currency_id._convert(move.amount_wht, self.company_id.currency_id, self.company_id, self.payment_date),
                'balance' : move.currency_id._convert(move.amount_residual, self.company_id.currency_id, self.company_id, self.payment_date),
                'currency_id' : self.currency_id.id,
                'paid_amount': move.currency_id._convert(paid_amount, self.company_id.currency_id, self.company_id, self.payment_date),
            }))
        payment_vals['invoice_line'] = val
        return payment_vals

    def _create_payments(self):
        self.ensure_one()
        all_batches = self._get_batches()
        batches = []
        # Skip batches that are not valid (bank account not trusted but required)
        for batch in all_batches:
            batch_account = self._get_batch_account(batch)
            if self.require_partner_bank_account and not batch_account.allow_out_payment:
                continue
            batches.append(batch)

        if not batches:
            raise UserError(_('To record payments with %s, the recipient bank account must be manually validated. You should go on the partner bank account in order to validate it.', self.payment_method_line_id.name))

        first_batch_result = batches[0]
        edit_mode = self.can_edit_wizard and (len(first_batch_result['lines']) == 1 or self.group_payment)
        to_process = []

        if edit_mode:
            payment_vals = self._create_payment_vals_from_wizard(first_batch_result)
            to_process.append({
                'create_vals': payment_vals,
                'to_reconcile': first_batch_result['lines'],
                'batch': first_batch_result,
            })
        else:
            # Don't group payments: Create one batch per move.
            if not self.group_payment:
                new_batches = []
                for batch_result in batches:
                    for line in batch_result['lines']:
                        new_batches.append({
                            **batch_result,
                            'payment_values': {
                                **batch_result['payment_values'],
                                'payment_type': 'inbound' if line.balance > 0 else 'outbound'
                            },
                            'lines': line,
                        })
                batches = new_batches

            for batch_result in batches:
                to_process.append({
                    'create_vals': self._create_payment_vals_from_batch(batch_result),
                    'to_reconcile': batch_result['lines'],
                    'batch': batch_result,
                })

        payments = self._init_payments(to_process, edit_mode=edit_mode)
#         self._post_payments(to_process, edit_mode=edit_mode)
#         self._reconcile_payments(to_process, edit_mode=edit_mode)
        return payments

    def action_create_payments(self):
        payments = self._create_payments()

#         if self._context.get('dont_redirect_to_payments'):
#             return True

        action = {
            'name': _('Payments'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.payment',
            'context': {'create': False},
        }
        if len(payments) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': payments.id,
            })
        else:
            action.update({
                'view_mode': 'tree,form',
                'domain': [('id', 'in', payments.ids)],
            })
        return action
