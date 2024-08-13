# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from datetime import datetime
from odoo.exceptions import UserError
import calendar


class MoveLine(models.Model):
    _inherit = 'account.move.line'

    def _selection_year(self):
        """docstring for fname"""
        return [(num, str(num)) for num in range(2000, (datetime.now().year)+2 )]

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
        selection=[(str(num), str(num)) for num in range(2000, (datetime.now().year)+3 )],
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
    reverse_move_id = fields.Many2one(
        comodel_name='account.move',
        string='Reverse Move',
    )

    def _compute_defer_vat(self):
        """docstring for _compute_defer_vat"""
        for rec in self:
            tax_line_id = rec.tax_line_id
            if rec.move_id.state != 'posted' or (tax_line_id.use_suspend_vat):
                rec.deffer_vat = True
            else:
                rec.deffer_vat = False
#             vat_purchase = False
#             account_purchase_tax_id = rec.move_id.company_id.account_purchase_tax_id
#             for l in account_purchase_tax_id.invoice_repartition_line_ids:
#                 if l.account_id:
#                     vat_purchase = l.account_id
#             if vat_purchase and rec.account_id == vat_purchase:
#                 rec.deffer_vat = False
#             else:
#                 rec.deffer_vat = True

    def get_reverse_vat_move_line(self, date):
        """docstring for get_reverse_vat_move_line"""
#         def get_reverse_vat_move_line(self,move_id,tax_suspend,date):
        aml_obj = self.env['account.move.line'].with_context(check_move_validity=False)
        partner = None
        refund = False
        if self.move_id:
            partner = self.move_id.partner_id.id
            if self.move_id.move_type == 'in_refund':
                refund = True
        else:
            partner = None
#         if self.account_move_line_id and self.account_move_line_id.debit == 0:
#             refund = True
        aml = []
        aml.append((0, 0, {
            'name': 'Tax Waiting Bill',
            'debit': self.amount_currency if refund else 0,
            'credit' : self.amount_currency if not refund else 0,
            'account_id' : self.account_id.id,
            'partner_id': partner,
            'date': date,
        }))
        aml.append((0, 0, {
            'name' : 'Input Tax',
            'debit' : self.amount_currency if not refund else 0,
            'credit' : self.amount_currency if refund else 0,
            'account_id' : self.tax_line_id.tax_suspend_id.get_tax_tax(),
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

    def verify_tax(self):
        """docstring for verify_tax"""
        for rec in self:
            if not rec.month_vat or not rec.year:
                raise UserError(_('Please Insert Detail of Vat Use'))
            rec.is_verify = True
#             if not rec.reverse_move_id and rec.tax_line_id.use_suspend_vat and\
#                 not rec.tax_line_id.tax_suspend_id.use_suspend_vat:
#                 ref = rec.move_id.name
#                 rec.create_move_reverse(ref)

    def unverify_tax(self):
        """docstring for unverify_tax"""
        for rec in self:
            if rec.reverse_move_id:
                move = rec.reverse_move_id
                move.button_draft()
                move.unlink()
            rec.is_verify = False

    def _stock_account_get_anglo_saxon_price_unit(self):
        """docstring for _stock_account_get_anglo_saxon_price_unit"""
        res = super(MoveLine, self)._stock_account_get_anglo_saxon_price_unit()
        self_qty = self.quantity
        product = self.product_id
        origin = self.move_id.invoice_origin
        sos = self.env['sale.order'].search([('name', '=', origin)])
        pick_name = False
        for pick in sos.picking_ids:
            for move in pick.move_line_ids_without_package:
                if move.product_id.id == product.id and move.qty_done == self_qty:
                    pick_name = pick.name
        if pick_name:
            for svl in product.stock_valuation_layer_ids:
                if pick_name in svl.description:
                    unitprice = svl.unit_cost
                    res = unitprice
#         product.stock_valuation_layer_ids.filtered(lambda x: abs(x.quantity) == self_qty)
        return res

