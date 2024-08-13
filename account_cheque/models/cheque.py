# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from datetime import datetime
from odoo.exceptions import ValidationError
import time


class account_cheque(models.Model):

    _name = "account.cheque"
    _inherit = ['mail.thread']
    _description = "cheque for customer payment and supplier payment"

    def _get_voucher_line(self):
        res = {}
        for cheque in self:
            id = cheque.id
            res[id]=[]
            if not cheque.id:
                continue
            partial_ids = []
            for payment in cheque.payment_line:
                partial_ids.append(payment.voucher_id.id)
            res[id] = [x for x in partial_ids]
        return res

    def _get_deposit_line(self):
        res = {}
        for cheque in self:
            id = cheque.id
            res[id]=[]
            if not cheque.id:
                continue
            partial_ids = []
            for payment in cheque.payment_line:
                partial_ids.append(payment.payment_id.id)
            res[id] = [x for x in partial_ids]
        return res

    def _get_move_lines(self):
        res = {}
        for invoice in self:
            id = invoice.id
            res[id] = []
            if not invoice.move_id:
                continue
            data_lines = [x for x in invoice.move_id.line_id]
            partial_ids = []
            for line in data_lines:
                partial_ids.append(line.id)
            res[id] =[x for x in partial_ids]
        return res

    name = fields.Char('Cheque No.', size=32, required=True,copy=False,tracking=1)
    cheque_date = fields.Date('Cheque Date',required=True,tracking=1)
    bank = fields.Many2one('res.bank', 'Bank',required=False)
    partner_id = fields.Many2one('res.partner', 'Pay', required=True, ondelete='cascade', index=True,tracking=1)
    amount = fields.Float('Amount', digits="Product Price", required=True,tracking=1)
    type = fields.Selection([('out', 'Supplier'), ('in', 'Customer')], 'Cheque Type', required=True, index=True)
    note = fields.Text('Notes')
    date_cancel = fields.Datetime('Date Cancel')
    date_done = fields.Date('Date Done',tracking=1)
    date_pending = fields.Datetime('Date Pending')
    date_reject = fields.Datetime('Date Reject')
    date_assigned = fields.Datetime('Date Assigned')
    date_receipt = fields.Date('Date Receive')
    account_receipt_id = fields.Many2one('account.account','Account Receive',tracking=1)
    account_pay_id = fields.Many2one('account.account','Account Payable')
    journal_id = fields.Many2one('account.journal', 'Journal', readonly=False,tracking=1)
    move_id = fields.Many2one('account.move', 'Account Entry')
    move_name = fields.Char(related='move_id.name', string='Account Entry Name', readonly=True,tracking=1)
    move_ref = fields.Char(related='move_id.ref', string='Account Entry Ref', readonly=True)
    account_move_lines = fields.Many2many(compute="_get_move_lines", comodel_name='account.move.line', string='General Ledgers')
    active = fields.Boolean('Active', default=True)
    cheque_id = fields.Many2one('account.cheque', 'Cheque Return', readonly=False)
    payment_method_id = fields.Many2one('account.payment.method.multi',ondelete="cascade", string='Payment Method', tracking=1, required=False)
    company_id = fields.Many2one(
        'res.company',
        'Company',
        required=True,
        default=lambda self: self.env.company,
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('cancel', 'Cancelled'),
        ('assigned', 'Assigned'),
        ('reject', 'Reject'),
        ('done', 'Done'),
        ], 'Status', readonly=True, index=True, tracking=1,default='draft'
    )
    journal_count = fields.Integer(
        string='# of Journal',
        compute='_get_count_journal',
        readonly=True
    )
    payment_count = fields.Integer(
        string='# of Payment',
        compute='_get_count_payment',
        readonly=True
    )

    _sql_constraints = [
        ('name_unique', 'unique (name,company_id)', 'Cheque No. must be unique !')
    ]

    def _get_count_journal(self):
        for rec in self:
            rec.update({'journal_count': len(rec.len_move_id())})

    def _get_count_payment(self):
        """docstring for _get_count_payment"""
        for rec in self:
            payment = self.env['account.payment'].search([('cheque_ids', 'in', [rec.id])])
            rec.payment_count = len(payment)

    def len_move_id(self):
        len_move = []
        if self.move_ref:
            account_move_search = self.env['account.move'].search([
                    ('ref', '=', self.move_ref),
                ])
            for move in account_move_search:
                len_move.append(move.id)
                reverse_move = self.env['account.move'].search([
                    ('ref', 'like', move.name)
                ])
                if reverse_move:
                    len_move.append(reverse_move.id)
        return len_move

    def action_view_payment(self):
        moves = self.env['account.payment'].search([('cheque_ids', 'in', self.ids)])
        action = self.sudo().env.ref('account.action_account_payments').read()[0]
        if len(moves) > 1:
            action['domain'] = [('id', 'in', moves.ids)]
        elif len(moves) == 1:
            action['views'] = [(self.env.ref('account.view_account_payment_form').id, 'form')]
            action['res_id'] = moves.id
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    def action_view_journal(self):
        moves = self.len_move_id()
        action = self.sudo().env.ref('account.action_move_journal_line').read()[0]
        if len(moves) > 1:
            action['domain'] = [('id', 'in', moves)]
        elif len(moves) == 1:
#             action['views'] = [(self.env.ref('account.view_move_form').id, 'form')]
            action['domain'] = [('id', 'in', moves)]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    def action_cancel_draft(self):
        text = "--> to Edit"
        if self.move_id:
            self.move_id.narration = self.move_id.narration + "%s" %text
            self.move_id = ''
        self.write({'state':'draft'})
        return True

    def action_done(self):

        move_pool = self.env['account.move']
        move_line_pool = self.env['account.move.line']

        for line in self:
            if line.date_done < line.date_receipt:
                raise ValidationError('Please Check date done')
            if not line.date_done:
                raise ValidationError('Please define date done before Done Cheque.')
            if not line.journal_id:
                raise ValidationError('Please define Journal before Done Cheque.')
            ctx = {}
            date_done = line.date_done
            if self.move_id:
                move_id = self.move_id
            elif line.type == 'in':

                ctx.update({'date': line.date_done})
#                 gl_name = self.env['ir.sequence'].with_context(ir_sequence_date=date_done).next_by_code('account.cheque.in')
                detail = u'เช็ครับผ่าน '+line.partner_id.name +u' เลขที่เช็ค '+str(line.name)
                vals = []

                vals.append([0, 0, {
                                'name': detail,
                                'debit': line.amount,
                                'credit': 0.0,
                                'date': line.date_done,
                                'account_id': line.account_receipt_id.id,
                                'journal_id': line.journal_id.id,
                                'partner_id': line.partner_id.id,
                }])

                vals.append([0, 0, {
                                'name': line.journal_id.cheque_income_account_id.name or line.journal_id.cheque_income_account_id.name,
                                'debit': 0.0,
                                'credit': line.amount,
                                'account_id': line.journal_id.cheque_income_account_id.id or line.journal_id.cheque_income_account_id.id,
                                'date': line.date_done,
                                'journal_id': line.journal_id.id,
                                'partner_id': line.partner_id.id,
                }])
                move_cheque = {
#                     'name': gl_name,
                    'ref': line.name,
                    'date': line.date_done,
                    'journal_id': line.journal_id.id,
                    'narration': detail,
                    'partner_id': line.partner_id.id,
                    'line_ids' : vals,
                }
                move_id = move_pool.create(move_cheque)
            else:
                ctx.update({'date': line.date_done})
#                 gl_name = self.env['ir.sequence'].with_context(ir_sequence_date=date_done).next_by_code('account.cheque.out')
                detail = u'เช็คจ่ายผ่าน '+line.partner_id.name +u' เลขที่เช็ค '+str(line.name)
                vals = []

                vals.append([0, 0, {
                                'name': detail,
                                'date': line.date_done,
                                'debit': 0.0,
                                'credit': line.amount,
                                'account_id': line.account_pay_id.id,
                                'journal_id': line.journal_id.id,
                                'partner_id': line.partner_id.id,
                }])

                vals.append([0, 0, {
                                'name': line.journal_id.cheque_out_account_id.name or line.journal_id.cheque_out_account_id.name,
                                'date': line.date_done,
                                'debit': line.amount,
                                'credit': 0.0,
                                'account_id': line.journal_id.cheque_out_account_id.id or line.journal_id.cheque_out_account_id.id,
                                'journal_id': line.journal_id.id,
                                'partner_id': line.partner_id.id,
                }])

                move_cheque = {
#                     'name': gl_name,
                    'ref':  line.name,
                    'date': line.date_done,
                    'journal_id': line.journal_id.id,
                    'narration':detail,
                    'partner_id': line.partner_id.id,
                    "line_ids": vals,
                }
                move_id  = move_pool.create(move_cheque)

            move_id.action_post()
            self.write({'state':'done','move_id':move_id.id})
        return True

    def action_assigned(self):
        self.write({'state':'assigned'})
        return True

    def cancel_cheque(self):
        text = " --> Cancel Cheque"
        if self.move_id:
            self.move_id.narration = self.move_id.narration + "%s" %text
        self.write({'state':'cancel','date_cancel': time.strftime('%Y-%m-%d %H:%M:%S')})
        return True

    def reject_cheque(self):
        cheq = self.browse([])
#         copy_id= self.copy(default={'name':cheq.name+'(copy)'})
#         self.write({'state':'reject','date_reject': time.strftime('%Y-%m-%d %H:%M:%S'),'cheque_id':copy_id})
        self.write({
            'state':'reject',
            'date_reject': time.strftime('%Y-%m-%d %H:%M:%S')
        })
#         view_ref = self.env['ir.model.data'].get_object_reference('tr_standard_account', 'view_tr_cheque_form')
#         view_id = view_ref and view_ref[1] or False,
#         return {
#             'type': 'ir.actions.act_window',
#             'name': 'Cheque',
#             'res_model': 'account.cheque',
#             'res_id': copy_id,
#             'view_type': 'form',
#             'view_mode': 'form',
#             'view_id': view_id,
#             'target': 'current',
#             'nodestroy': True,
#         }

    def cancel_cheque_done(self):
        self.write({'state': 'assigned'})
        self.move_id.state = 'cancel'
        self.move_id.unlink()
        return True


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
