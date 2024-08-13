# -*- coding: utf-8 -*-

from odoo import fields, models, api, _, Command
from odoo.exceptions import UserError, ValidationError

MAP_INVOICE_TYPE_PARTNER_TYPE = {
    'out_invoice': 'customer',
    'out_refund': 'customer',
    'in_invoice': 'supplier',
    'in_refund': 'supplier',
}

MAP_TYPE_PAYMENT_SIGN = {
    'inbound': -1,
    'outbound': 1,
}

class AccountPayment(models.Model):
    _inherit ='account.payment'

    @api.depends('invoice_line.paid_amount')
    def _compute_invoice(self):
        payment = self
        payment.invoice_total = sum(line.paid_amount for line in payment.invoice_line)
        payment.wht_total = sum(line.paid_total for line in payment.payment_line if line.wht_id)


    payment_line = fields.One2many(
        'account.payment.line',
        'payment_id',
        string = 'Payment Detail'
    )
    invoice_line = fields.One2many(
        'account.invoice.payment.line',
        'payment_id',
        string = 'Invoice Line Detail'
    )
    other_amount = fields.Float(
        string='Other Amount',
        compute='_compute_other_amount',
    )
    invoice_total = fields.Monetary(
        compute = '_compute_invoice',
        string = 'Amount Invoice'
    )
    wht_total = fields.Monetary(
        compute='_compute_invoice',
        string='WHT Total'
    )
    tax_invoice_number = fields.Char(
        string="Tax Invoice Number",
        required=False,
    )
    tax_invoice_date = fields.Date(
        string="Tax Invoice Date",
        required=False,
    )
    move_id = fields.Many2one(
        'account.move',
        string='Journal Entry',
        readonly=True,
        index=True,
        ondelete='restrict',
        copy=False,
        help="Link to the automatically generated Journal Items.")
    payment_method_id = fields.Many2one(
        required=False,
    )
    payment_type = fields.Selection(
        required=False
    )
    relate_move_id = fields.Many2one(
        related='move_id',
        string='Journal Entry Relate',
    )
    comment = fields.Text(
        string='Additional Information',
    )
    total_amount = fields.Float(
        string='Total Amount',
        compute='_compute_total_amount',
    )
    ### Cheque ###
    is_cheque = fields.Boolean(
        string='Is Cheque',
        related='journal_id.is_cheque',
    )
    cheque_number = fields.Char(
        string='Cheque Number',
    )
    cheque_date = fields.Date(
        string='Cheque Date',
    )
    cheque_ids = fields.Many2many(
        comodel_name='account.cheque',
        string='Cheques',
        domain="[('state', '=','draft')]",
    )

    @api.depends('invoice_total','other_amount')
    def _compute_total_amount(self):
        """docstring for _compute_total_amount"""
        for rec in self:
            total_amount = rec.invoice_total
            if rec.payment_type == 'inbound':
                for line in rec.payment_line:
                    if line.wht_id:
                        total_amount -= line.paid_total
                    else:
                        total_amount -= line.paid_total
            elif rec.payment_type == 'outbound':
                for line in rec.payment_line:
                    if line.wht_id:
                        total_amount -= line.paid_total
                    else:
                        total_amount += line.paid_total
            rec.total_amount = total_amount

    @api.depends('payment_line.paid_total')
    def _compute_other_amount(self):
        """docstring for _compute_other_amount"""
        for rec in self:
            rec.other_amount = 0
            for line in rec.payment_line:
                rec.other_amount += line.paid_total

    @api.onchange('total_amount')
    def onchange_invoice_total(self):
        """docstring for onchange_invoice_total"""
        for rec in self:
            rec.amount = rec.total_amount

    def get_payment_line(self,invoice_line):
        val = []
        for invoice in invoice_line:
#             if self.currency_id != invoice.currency_id:
#                 currency = invoice.currency_id.with_context(date=invoice.date_invoice or fields.Date.context_today(self))
#                 residual = currency.compute(invoice.residual, self.company_id.currency_id)
            residual = invoice.amount_residual
            val.append((0, 0, {
                'invoice_id': invoice.id,
                'dute_date' : invoice.invoice_date_due,
                'amount' : invoice.amount_total,
                'wht_total': invoice.amount_wht,
                'balance' : residual or invoice.amount_residual,
                'currency_id' : invoice.currency_id.id,
            }))
        return val

    @api.onchange('partner_id','payment_type')
    def _onchange_partner(self):
        val = []
        type_invoice = self.payment_type == 'inbound' and 'out_invoice' or 'in_invoice'
        account_move = self.env['account.move']
        invoice_line = account_move.search([
            ('partner_id','=',self.partner_id.id),
            ('state','in',['posted']),
            ('amount_residual', '!=', 0),
            ('move_type','=',type_invoice)
        ])
        val = self.get_payment_line(invoice_line)
        self.invoice_line = val
#         return {'value': {'invoice_line': val},}

    @api.constrains('amount')
    def _check_amount(self):
        for rec in self:
            if rec.amount is False:
                raise ValidationError('The payment amount must be strictly positive.')

    @api.onchange('invoice_total')
    def onchange_invoice_line(self):
        self.amount = 0
        self.amount = self.invoice_total

    def _reconcile_payments(self):
        """docstring for _reconcile_payments"""
        for rec in self:
            move_lines = self.env['account.move.line']
            domain = [
                ('parent_state', '=', 'posted'),
                ('account_type', 'in', self.env['account.payment']._get_valid_payment_account_types()),
                ('reconciled', '=', False),
            ]
            move = rec.move_id
            payment_lines = move.line_ids.filtered_domain(domain)
            for line in rec.invoice_line:
                move_id = line.invoice_id
                move_lines |= move_id.line_ids.filtered_domain(domain)
            if move_lines and payment_lines:
                for account in payment_lines.account_id:
                    (payment_lines + move_lines)\
                    .filtered_domain([('account_id', '=', account.id), ('reconciled', '=', False)])\
                    .reconcile()


    def action_post(self):
        """docstring for action_post"""
        res = super().action_post()
        for rec in self:
            if rec.is_cheque:
                rec.create_cheque()
            rec._reconcile_payments()
        return res

    def create_cheque(self):
        if self.total_amount <= 0:
            raise UserError(_('Total Payment Method Not Less more Zero.'))

        if not self.cheque_number:
            raise UserError(_('Please insert Cheque number'))
        if not self.cheque_date:
            raise UserError(_('Please insert date   '))
        if self.payment_type == 'inbound':
            cheque_type = 'in'
            if not self.journal_id.cheque_income_account_id:
                raise UserError(_('Please insert Cheque Income Account'))
            account_id = self.journal_id.cheque_income_account_id.id

        else:
            cheque_type = 'out'
            if not self.journal_id.cheque_out_account_id:
                raise UserError(_('Please insert Cheque Out Account'))
            account_id = self.journal_id.cheque_out_account_id.id
        cheq = self.env['account.cheque'].search([('name', '=', self.cheque_number)])
        if cheq and not self.cheque_id:
            self.update({'cheque_ids': [(6, 0, cheq.ids)]})
        else:
            cheque_vals = {
                    'name': self.cheque_number,
                    'cheque_date': self.cheque_date,
                    'partner_id': self.partner_id.id,
                    'journal_id': self.journal_id.id,
                    'amount': self.total_amount,
                    'type': cheque_type,
                    'account_receipt_id': account_id,
                    'account_pay_id': account_id,
                    'payment_id' :self.id,
                }
            cheque_id = self.env['account.cheque'].create(cheque_vals)
            self.update({'cheque_ids': [(6, 0, cheque_id.ids)]})

    def check_suspend_vat(self,move_id):
        """Hook for check other invoice tax"""
        return True

    def get_old_movename(self):
        old_name = False
        return old_name

    def check_suspend_tax_ref(self):
        name = "Draft Payment"
        return name

    def check_is_use_same_journal_seq(self,rec_name):
        name = rec_name
        return name

    def _get_valid_liquidity_accounts(self):
        pay_met = self.env['account.payment.method.multi'].search([])
        acc_pay_mat = pay_met.mapped('account_id')
        return (
            self.journal_id.default_account_id |
            self.payment_method_line_id.payment_account_id |
            self.journal_id.company_id.account_journal_payment_debit_account_id |
            self.journal_id.company_id.account_journal_payment_credit_account_id |
            self.journal_id.inbound_payment_method_line_ids.payment_account_id |
            self.journal_id.outbound_payment_method_line_ids.payment_account_id |
            self.payment_line.payment_method_id.account_id |
            acc_pay_mat
        )

    def _prepare_move_line_default_vals(self, write_off_line_vals=None):
        ''' Prepare the dictionary to create the default account.move.lines for the current payment.
        :param write_off_line_vals: Optional list of dictionaries to create a write-off account.move.line easily containing:
            * amount:       The amount to be added to the counterpart amount.
            * name:         The label to set on the line.
            * account_id:   The account on which create the write-off.
        :return: A list of python dictionary to be passed to the account.move.line's 'create' method.
        '''
        self.ensure_one()
        write_off_line_vals = write_off_line_vals or {}
        comp = self.journal_id.company_id

        if not self.outstanding_account_id:
            raise UserError(_(
                "You can't create a new payment without an outstanding payments/receipts account set either on the company or the %s payment method in the %s journal.",
                self.payment_method_line_id.name, self.journal_id.display_name))

        # Compute amounts.
        write_off_line_vals_list = []
        for wol in write_off_line_vals:
            if wol['amount_currency'] != 0:
                write_off_line_vals_list.append(wol)
#                 del(wol)
#         if write_off_line_vals[0]['amount_currency'] == 0:
#             write_off_line_vals_list = []
#         else:
#         write_off_line_vals_list = write_off_line_vals or []
        write_off_amount_currency = sum(x['amount_currency'] for x in write_off_line_vals_list)
        write_off_balance = sum(x['balance'] for x in write_off_line_vals_list)

        if self.payment_type == 'inbound':
            # Receive money.
            liquidity_amount_currency = self.invoice_total
        elif self.payment_type == 'outbound':
            # Send money.
            liquidity_amount_currency = -self.invoice_total
        else:
            liquidity_amount_currency = 0.0

        liquidity_balance = self.currency_id._convert(
            liquidity_amount_currency,
            self.company_id.currency_id,
            self.company_id,
            self.date,
        )
        counterpart_amount_currency = -liquidity_amount_currency - write_off_amount_currency
        counterpart_balance = -liquidity_balance - write_off_balance
        currency_id = self.currency_id.id

        # Compute a default label to set on the journal items.
        liquidity_line_name = ''.join(x[1] for x in self._get_liquidity_aml_display_name_list())
        counterpart_line_name = ''.join(x[1] for x in self._get_counterpart_aml_display_name_list())

        line_vals_list = [
            # Liquidity line.
#             {
#                 'name': liquidity_line_name,
#                 'date_maturity': self.date,
#                 'amount_currency': liquidity_amount_currency,
#                 'currency_id': currency_id,
#                 'debit': liquidity_balance if liquidity_balance > 0.0 else 0.0,
#                 'credit': -liquidity_balance if liquidity_balance < 0.0 else 0.0,
#                 'partner_id': self.partner_id.id,
#                 'account_id': self.outstanding_account_id.id,
#             },
            # Receivable / Payable.
            {
                'name': counterpart_line_name,
                'date_maturity': self.date,
                'amount_currency': counterpart_amount_currency,
                'currency_id': currency_id,
                'debit': counterpart_balance if counterpart_balance > 0.0 else 0.0,
                'credit': -counterpart_balance if counterpart_balance < 0.0 else 0.0,
                'partner_id': self.partner_id.id,
                'account_id': self.destination_account_id.id,
            },
        ]
        payment_amt = 0
        pay_wht = 0
        if self.payment_line:
            for pay_line in self.payment_line:
                paid_amt = pay_line.paid_total
#                 if self.payment_type == 'inbound': #sale
#                     paid_amt = pay_line.paid_total
#                 elif self.payment_type == 'outbound': #purchase
#                     paid_amt = -pay_line.paid_total
                if self.payment_type == 'outbound' and pay_line.payment_method_id.type == 'wht': #purchase
                    paid_amt = -(abs(pay_line.paid_total))
                    payment_amt += paid_amt
                else:
                    payment_amt += pay_line.paid_total
                acc_id = pay_line.payment_method_id.account_id.id
                put_select_account = pay_line.payment_method_id.put_select_account
                if put_select_account == 'debit':
                    debit = paid_amt
                    credit = 0
                else:
                    debit = 0
                    credit = paid_amt
                line_vals_list += [{
                    'name': pay_line.payment_method_id.name,
                    'date_maturity': self.date,
                    'amount_currency': paid_amt,
                    'currency_id': currency_id,
#                     'debit': debit,
#                     'credit': credit,
                    'debit': paid_amt if paid_amt > 0.0 else 0.0,
                    'credit': -paid_amt if paid_amt < 0.0 else 0.0,
                    'partner_id': self.partner_id.id,
                    'account_id': acc_id,
                }]
#         if self.payment_type == 'inbound':
#             oust_amt = liquidity_balance - payment_amt
#         elif self.payment_type == 'outbound':
        oust_amt = liquidity_balance - payment_amt
#         if self.payment_type == 'outbound' and pay_line.payment_method_id.type == 'wht': #purchase
#             oust_amt = oust_amt + pay_wht
        if comp.non_reconcile:
            acc_liq = self.journal_id.default_account_id.id
            if self.journal_id.is_cheque:
                if self.payment_type == 'inbound':
                    acc_liq = self.journal_id.cheque_income_account_id.id
                elif self.payment_type == 'outbound':
                    acc_liq = self.journal_id.cheque_out_account_id.id
        else:
            acc_liq = self.outstanding_account_id.id
        if oust_amt != 0:
            line_vals_list += [{
                'name': liquidity_line_name,
                'date_maturity': self.date,
                'amount_currency': oust_amt,
                'currency_id': currency_id,
                'debit': oust_amt if oust_amt > 0.0 else 0.0,
                'credit': -oust_amt if oust_amt < 0.0 else 0.0,
                'partner_id': self.partner_id.id,
                'account_id': acc_liq,
            }]
        return line_vals_list + write_off_line_vals_list

    def _synchronize_to_moves(self, changed_fields):
        ''' Update the account.move regarding the modified account.payment.
        :param changed_fields: A list containing all modified fields on account.payment.
        '''
        if self._context.get('skip_account_move_synchronization'):
            return

        if not any(field_name in changed_fields for field_name in self._get_trigger_fields_to_synchronize()):
            return

        for pay in self.with_context(skip_account_move_synchronization=True):
            liquidity_lines, counterpart_lines, writeoff_lines = pay._seek_for_lines()

            # Make sure to preserve the write-off amount.
            # This allows to create a new payment with custom 'line_ids'.

            write_off_line_vals = []
            if liquidity_lines and counterpart_lines and writeoff_lines:
                write_off_line_vals.append({
                    'name': writeoff_lines[0].name,
                    'account_id': writeoff_lines[0].account_id.id,
                    'partner_id': writeoff_lines[0].partner_id.id,
                    'currency_id': writeoff_lines[0].currency_id.id,
                    'amount_currency': sum(writeoff_lines.mapped('amount_currency')),
                    'balance': sum(writeoff_lines.mapped('balance')),
                })

            line_vals_list = pay._prepare_move_line_default_vals(write_off_line_vals=write_off_line_vals)
            line_ids_commands = []
            for lnv in line_vals_list:
                line_ids_commands += [
                    Command.create(lnv)
                ]
#                 for liq in liquidity_lines:
#                     line_ids_commands += [
#                         Command.update(liq.id, line_vals_list[0]) if liquidity_lines else Command.create(line_vals_list[0]),
#                     ]

#             line_ids_commands = [
#                 Command.update(liquidity_lines.id, line_vals_list[0]) if liquidity_lines else Command.create(line_vals_list[0]),
#                 Command.update(counterpart_lines.id, line_vals_list[1]) if counterpart_lines else Command.create(line_vals_list[1])
#             ]

            for liq in liquidity_lines:
                line_ids_commands.append((2, liq.id))
            for col in counterpart_lines:
                line_ids_commands.append((2, col.id))
            for line in writeoff_lines:
                line_ids_commands.append((2, line.id))

#             for extra_line_vals in line_vals_list[2:]:
#                 line_ids_commands.append((0, 0, extra_line_vals))

            # Update the existing journal items.
            # If dealing with multiple write-off lines, they are dropped and a new one is generated.

            pay.move_id\
                .with_context(skip_invoice_sync=True)\
                .write({
                    'partner_id': pay.partner_id.id,
                    'currency_id': pay.currency_id.id,
                    'partner_bank_id': pay.partner_bank_id.id,
                    'line_ids': line_ids_commands,
                })

    def _synchronize_from_moves(self, changed_fields):
        return True
