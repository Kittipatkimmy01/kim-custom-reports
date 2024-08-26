# -*- coding: utf-8 -*-
from bahttext import bahttext
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AccountBilling(models.Model):
    _name = 'account.billing'
    _inherit = ['mail.activity.mixin', 'mail.thread']
    _description = 'Account Billing'
    _order = 'name desc'

    name = fields.Char(
        string='Name',
        default='Draft',
    )

    bill_date = fields.Date(
        string='Bill Date',
        default=fields.Date.today(),
        required=True,
    )

    payment_term_id = fields.Many2one(
        'account.payment.term',
        string='Payment Term'
    )

    partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
        required=True,
    )

    line_ids = fields.One2many(
        'account.billing.line',
        'billing_id',
        string='Billing Line',
    )

    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('posted', 'Posted'),
            ('cancel', 'Cancelled'),
        ],
        string='Status',
        required=True, readonly=True, copy=False, tracking=True,
        default='draft'
    )

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True, readonly=True,
        default=lambda self: self.env.company or self.env.user.company_id
    )

    currency_id = fields.Many2one(
        'res.currency',
        related='company_id.currency_id',
        store=True,
        related_sudo=False
    )

    move_ids = fields.Many2many(
        'account.move',
        'account_move_billing_rel',
        compute='_compute_move_ids'
    )

    amount_total = fields.Monetary(
        compute='_compute_amount',
        string='Total',
        currency_field='currency_id'
    )

    currency_id = fields.Many2one(
        'res.currency',
        default=lambda x: x.env.company.currency_id.id,
    )

    notes = fields.Text(
        string='Notes'
    )

    is_hide_register = fields.Boolean(
        compute='_compute_is_hide_register'
    )

    def _compute_is_hide_register(self):
        for rec in self:
            rec.is_hide_register = True
            if any([
                'not_paid' in rec.move_ids.mapped('payment_state'),
                'partial' in rec.move_ids.mapped('payment_state'),
            ]):
                rec.is_hide_register = False

    @api.onchange('partner_id')
    def _onchange_partner(self):
        self.line_ids = False
        if self.partner_id and self.partner_id.property_payment_term_id:
            self.payment_term_id = self.partner_id.property_payment_term_id.id

    @api.depends('line_ids')
    def _compute_move_ids(self):
        for rec in self:
            rec.move_ids = [(6, 0, rec.line_ids.mapped('move_id').ids)]

    def action_register_payment(self):
        return self.move_ids.action_register_payment()
        
    def action_post(self):
        if not self.line_ids:
            raise ValidationError(_('Please fill order !'))
        if self.name == 'Draft':
            sequence = self.env['ir.sequence']
            if not sequence.search([('code', '=', 'account.billing'), ('company_id', '=', self.env.company.id)]):
                sequence.sudo().create({
                    'name': 'Billing Notes',
                    'code': 'account.billing',
                    'prefix': 'BL%(y)s%(range_month)s-',
                    'padding': 4,
                    'implementation': 'no_gap',
                    'company_id': self.env.company.id,
                    'use_date_range': True,
                    'range_reset': 'monthly',
                })
            self.name = sequence.next_by_code('account.billing', sequence_date=self.bill_date)
        self.write({'state': 'posted'})

    def button_cancel(self):
        self.write({'state': 'cancel'})

    def button_draft(self):
        self.write({'state': 'draft'})

    @api.depends('line_ids')
    def _compute_amount(self):
        for rec in self:
            amt_total  = sum(rec.line_ids.mapped('amount_manual'))
            if amt_total == 0:
                amt_total = sum(rec.line_ids.mapped('amount_total'))
            rec.amount_total = amt_total

    def get_amount_bahttext(self, amount):
        return bahttext(amount)

    def get_date(self, date):
        if date:
            string_date = str(date).split('-')[::-1]
            string_date[2] = str(int(string_date[2]) + 543)
            return '/'.join(string_date)
        return ''


class AccountBillingLine(models.Model):
    _name = 'account.billing.line'
    _description = 'Account Billing Line'

    billing_id = fields.Many2one(
        'account.billing',
        string='Billing',
    )

    move_id = fields.Many2one(
        'account.move',
        string='Invoices',
        required=True,
    )

    payment_state = fields.Selection(
        related='move_id.payment_state'
    )

    invoice_date = fields.Date(
        related='move_id.invoice_date',
        string='Invoice Date',
    )

    invoice_date_due = fields.Date(
        related='move_id.invoice_date_due',
        string='Due Date',
    )

    invoice_payment_term_id = fields.Many2one(
        'account.payment.term',
        related='move_id.invoice_payment_term_id',
    )

    currency_id = fields.Many2one(
        'res.currency',
        related='move_id.currency_id',
        store=True,
        related_sudo=False
    )

    amount_total = fields.Monetary(
        compute='_compute_amount',
        string='Total',
        store=True,
        currency_field='currency_id'
    )

    notes = fields.Text(
        string='Notes'
    )

    amount_manual = fields.Float(
        string='Total Manual',
    )

    @api.depends('move_id')
    def _compute_amount(self):
        for rec in self:
            rec.amount_total = False
            if rec.move_id.amount_residual:
                rec.amount_total = rec.move_id.amount_residual
                if rec.move_id.move_type == 'out_refund':
                    rec.amount_total = rec.amount_total * -1
                    rec.amount_manual = rec.amount_total * -1
