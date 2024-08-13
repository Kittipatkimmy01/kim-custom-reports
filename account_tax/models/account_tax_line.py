# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import datetime
import calendar


class AccountTax(models.Model):
    _inherit = 'account.tax'

    use_suspend_vat = fields.Boolean(
        string="Use Suspend Vat",
    )
    tax_suspend_id = fields.Many2one(
        comodel_name="account.tax",
        string="Vat Suspend Account",
        required=False,
    )
    auto_usevat_so = fields.Boolean(
        string='Auto use vat(sale)',
        default=True,
    )
    auto_usevat_po = fields.Boolean(
        string='Auto use vat(purchase)',
    )
    PP36 = fields.Boolean(
        string='PP36',
    )
    acc_vat36_id = fields.Many2one(
        comodel_name='account.account',
        string='Account Vat PP36',
    )

    def get_tax_tax(self):
        """docstring for get_tax_tax"""
        line_tax = self.invoice_repartition_line_ids.filtered(lambda x: x.repartition_type == 'tax')
        return line_tax.account_id.id


class AccountTaxLine(models.Model):
    _name = 'account.tax.line'
    _description = 'Account Tax Line'

    def _compute_base_amount(self):
        tax_grouped = {}
        for tax in self:
            tax.base = 0.0
            if tax.res_model and tax.res_id:
                tax_grouped = self.map_tax(tax_grouped)
            if tax.tax_id:
                key = self.get_grouping_key({
                    'tax_id': tax.tax_id.id,
                    'account_id': tax.account_id.id,
                })
                if tax.vat_ref:
                    key = self.add_invoice_ref_key(tax.vat_ref, key)
                tax.base = self.check_tax(tax, tax_grouped, key)
            else:
                _logger.warning('Tax Base Amount not computable probably due to a change in an underlying tax (%s).', tax.tax_id.name)

#     invoice_id = fields.Many2one('account.invoice', string='Invoice', ondelete='cascade', index=True)
    name = fields.Char(string='Tax Description', required=True)
    tax_id = fields.Many2one('account.tax', string='Tax', ondelete='restrict')
    tax_bill_id = fields.Many2one('account.tax', string='Tax Bill', ondelete='restrict')
    account_id = fields.Many2one('account.account', string='Tax Account', required=True, domain=[('deprecated', '=', False)])
    account_analytic_id = fields.Many2one('account.analytic.account', string='Analytic account')
    amount = fields.Monetary()
    manual = fields.Boolean(default=True)
    sequence = fields.Integer(help="Gives the sequence order when displaying a list of invoice tax.")
    company_id = fields.Many2one('res.company', string='Company', related='account_id.company_id', store=True, readonly=True)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', store=True, readonly=True)
    base = fields.Float(string='Base', compute='_compute_base_amount')
    date = fields.Date(
        string='Date',
    )
    month_vat = fields.Selection(
        selection=[
            ('1', 'January'),
            ('2', 'February'),
            ('3', 'March'),
            ('4', 'April'),
            ('5', 'May'),
            ('6', 'June'),
            ('7', 'July'),
            ('8', 'August'),
            ('9', 'September'),
            ('10', 'October'),
            ('11', 'November'),
            ('12', 'December'),
        ],
        string='Month of Vat',
    )
    year = fields.Selection(
        selection=[(str(num), str(num)) for num in range((datetime.now().year-5 ), (datetime.now().year)+3 )],
        string='Year',
        store=True,
    )
    vat_ref = fields.Char(
        string='Vat Reference',
    )
    deffer_vat = fields.Boolean(
        string='Is Deffer Vat',
        compute='_compute_defer_vat',
    )
    is_verify = fields.Boolean(
        string='Verify',
        default=False,
    )
    res_model = fields.Char(
        string='Res Model',
    )
    res_id = fields.Integer(
        string='Res ID',
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Partner',
    )
    reverse_move_id = fields.Many2one(
        comodel_name='account.move',
        string='Reverse Move',
    )

    def _compute_defer_vat(self):
        """docstring for _compute_defer_vat"""
        for rec in self:
            tax_line_id = rec.tax_id
            if tax_line_id.use_suspend_vat:
                rec.deffer_vat = True
            else:
                rec.deffer_vat = False
#             vat_purchase = False
#             account_purchase_tax_id = rec.company_id.account_purchase_tax_id
#             for l in account_purchase_tax_id.invoice_repartition_line_ids:
#                 if l.account_id:
#                     vat_purchase = l.account_id
#             if vat_purchase and rec.account_id == vat_purchase:
#                 rec.deffer_vat = False
#             else:
#                 rec.deffer_vat = True

    def get_reverse_vat_move_line(self, date):
        """docstring for get_reverse_vat_move_line"""
        partner = None
        refund = False
        partner = self.partner_id.id
        aml = []
        aml.append((0, 0, {
            'name': 'Tax Waiting Bill',
            'debit': self.amount if refund else 0,
            'credit' : self.amount if not refund else 0,
            'account_id' : self.account_id.id,
            'partner_id': partner,
            'date': date,
        }))
        aml.append((0, 0, {
            'name' : 'Input Tax',
            'debit' : self.amount if not refund else 0,
            'credit' : self.amount if refund else 0,
            'account_id' : self.tax_id.tax_suspend_id.get_tax_tax(),
            'partner_id' : partner,
            'date' :  date,
        }))
        return aml

    def get_rpv_move_reverse(self, date, ref):
        """docstring for get_rpv_move_reverse"""
        journal_rpv = self.env['account.journal'].search([('code', '=', 'RPV')])
        company_id = self.env.company
        if not journal_rpv:
            raise UserError(_('Please Create Journal for Reverse Purchase Vat'))
        move_line = self.get_reverse_vat_move_line(date=date)
        move_val = {
            'date': date,
            'ref': ref or '',
            'company_id': company_id.id,
            'journal_id': journal_rpv.id,
            'move_type': 'entry',
            'line_ids': move_line,
        }
        return move_val

    def create_move_reverse(self, ref):
        month = self.month_vat
        year = self.year
        day = calendar.monthrange(int(year), int(month))
        date = str(year) + '-' + str(month) + '-' + str(day[1])
        move_rpv = self.env['account.move'].create(self.get_rpv_move_reverse(date, ref))
        self.write({'reverse_move_id': move_rpv.id})
        move_rpv.post()
        return True

    def get_pp36_vat_move_line(self, date, journal):
        """docstring for get_pp36_vat_move_line"""
        partner = None
        partner = self.partner_id.id
        acc_vat36 = self.tax_bill_id.acc_vat36_id
        aml = []
        aml.append((0, 0, {
            'name': 'Tax RD',
            'debit': self.amount,
            'credit' : 0,
            'account_id' : self.account_id.id,
            'partner_id': partner,
            'date': date,
        }))
        aml.append((0, 0, {
            'name' : journal.name,
            'debit' : 0,
            'credit' : self.amount,
            'account_id' : journal.default_account_id.id,
            'partner_id' : partner,
            'date' :  date,
        }))
        aml.append((0, 0, {
            'name': 'Tax',
            'debit': self.amount,
            'credit' : 0,
            'account_id' : acc_vat36.id,
            'partner_id': partner,
            'date': date,
        }))
        aml.append((0, 0, {
            'name': 'Tax EX',
            'debit': 0,
            'credit' : self.amount,
            'account_id' : self.tax_bill_id.get_tax_tax(),
            'partner_id': partner,
            'date': date,
        }))
        return aml

    def get_pp36_move_reverse(self, date, ref, wiz):
        """docstring for get_pp36_move_reverse"""
        journal = wiz.journal_id
        company_id = self.env.company
        move_line = self.get_pp36_vat_move_line(date=date, journal=journal)
        move_val = {
            'date': date,
            'ref': ref or '',
            'company_id': company_id.id,
            'journal_id': journal.id,
            'move_type': 'entry',
            'line_ids': move_line,
        }
        return move_val

    def create_move_pp36(self, wiz):
        date = wiz.date
        ref = wiz.vat_ref
        move_rpv = self.env['account.move'].create(self.get_pp36_move_reverse(date, ref, wiz))
        self.write({'reverse_move_id': move_rpv.id})
        move_rpv.action_post()
        return True

    def verify_tax(self):
        """docstring for verify_tax"""
        for rec in self:
            if rec.tax_id.PP36:
                return {
                    'type': 'ir.actions.act_window',
                    'res_model': 'wizard.clear.pp36',
                    'view_mode': 'form',
                    'target': 'new',
                }
            else:
                if not rec.month_vat or not rec.year:
                    raise UserError(_('Please Insert Detail of Vat Use'))
                rec.is_verify = True
#             if not rec.reverse_move_id and rec.tax_id.use_suspend_vat and\
#                 not rec.tax_id.tax_suspend_id.use_suspend_vat:
#                 if rec.res_model == 'account.payment.order':
#                     if rec.payorder_tax_id.state not in ('generated', 'uploaded'):
#                         raise UserError(_('Cannot Use Vat in this State %s' % rec.payorder_tax_id.state))
#                     ref = rec.payorder_tax_id.name
#                 elif rec.res_model == 'account.petty.payment':
#                     if rec.petty_tax_id.state != 'posted':
#                         raise UserError(_('Cannot Use Vat in this State %s' % rec.payorder_tax_id.state))
#                     ref = rec.petty_tax_id.number
#                 elif rec.res_model == 'hr.expense.sheet':
#                     if rec.expense_tax_id.state not in ('post', 'done'):
#                         raise UserError(_('Cannot Use Vat in this State %s' % rec.expense_tax_id.state))
#                     ref = rec.expense_tax_id.number
#                 else:
#                     ref = 'Reverse Tax'
#                 rec.create_move_reverse(ref)
 
    def unverify_tax(self):
        """docstring for unverify_tax"""
        for rec in self:
            if rec.reverse_move_id:
                move = rec.reverse_move_id
                move.button_draft()
                move.unlink()
            rec.is_verify = False

    def map_tax(self, tax_grouped):
        return tax_grouped

    def check_tax(self, tax, tax_grouped, key):
        return 0.0

    def get_grouping_key(self, invoice_tax_val):
        """ Returns a string that will be used to group account.invoice.tax sharing the same properties"""
#         self.ensure_one()
        return str(invoice_tax_val['tax_id']) + '-' + str(invoice_tax_val['account_id'])

    def add_invoice_ref_key(self, ref, key):
        """Hook for check other invoice tax"""
        key = key + '-' + str(ref)
        return key

#     # DO NOT FORWARD-PORT!!! ONLY FOR v10
#     @api.model
#     def create(self, vals):
#         inv_tax = super(AccountInvoiceTax, self).create(vals)
#         # Workaround to make sure the tax amount is rounded to the currency precision since the ORM
#         # won't round it automatically at creation.
#         if inv_tax.company_id.tax_calculation_rounding_method == 'round_globally':
#             inv_tax.amount = inv_tax.currency_id.round(inv_tax.amount)
#         return inv_tax
