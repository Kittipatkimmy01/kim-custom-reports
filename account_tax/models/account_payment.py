# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class AccountTaxLine(models.Model):
    _inherit = 'account.tax.line'

    payment_tax_id = fields.Many2one(
        'account.payment',
        string='Account Payment',
        ondelete='cascade',
        index=True
    )

    def map_tax(self, tax_grouped):
        tax_grouped = super().map_tax(tax_grouped)
        for petty in self.mapped('payment_tax_id'):
            tax_grouped[petty.id] = petty.get_taxes_values()
        return tax_grouped

    def check_tax(self, tax, tax_grouped, key):
        tax_base = super().check_tax(tax, tax_grouped, key)
#         tax_base = 0.0
        if tax.payment_tax_id and key in tax_grouped[tax.payment_tax_id.id]:
            tax_base = tax_grouped[tax.payment_tax_id.id][key]['base']
        """Hook for check other invoice tax"""
        return tax_base

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    tax_line_ids = fields.One2many(
        comodel_name='account.tax.line',
        inverse_name='payment_tax_id',
        string='Tax Lines',
        copy=False
    )
    vat_ref = fields.Char(
        string='Vat Reference',
    )

    def action_draft(self):
        for tax in self.tax_line_ids:
            tax.unverify_tax()
        res = super().action_draft()
        return res

    def action_post(self):
        res = super().action_post()
        for rec in self:
            for line in rec.tax_line_ids:
                if (rec.payment_type == 'inbound' and line.tax_id.auto_usevat_so) or\
                    (rec.payment_type == 'outbound' and line.tax_id.auto_usevat_po):
                    line.is_verify = True
#                 line.verify_tax()
        return res

    def get_tax_ml_val(self, tax, date):
        """docstring for get_tax_ml_val"""
        refund = False
        if tax.tax_id.PP36:
            refund = True
        partner = tax.partner_id.id
        tax_ml_credit = {
            'name': 'Tax EX',
            'debit': tax.amount if refund else 0,
            'credit' : tax.amount if not refund else 0,
            'account_id' : tax.tax_bill_id.get_tax_tax(),
            'partner_id': partner,
            'date': date,
        }
        tax_ml_dedit = {
            'name': 'Tax RD',
            'debit': tax.amount if not refund else 0,
            'credit' : tax.amount if refund else 0,
            'account_id' : tax.tax_id.get_tax_tax(),
            'partner_id': partner,
            'date': date,
        }
        return tax_ml_credit, tax_ml_dedit

    def _prepare_move(self, bank_lines=None):
        """docstring for _prepare_move"""
        res = super(AccountPayment, self)._prepare_move(bank_lines)
        for tax in self.tax_line_ids:
            date = self.date_scheduled
            tax_ml_credit, tax_ml_dedit = self.get_tax_ml_val(tax, date)
            res['line_ids'].append((0, 0, tax_ml_credit))
            res['line_ids'].append((0, 0, tax_ml_dedit))
        return res

    def _prepare_move_line_default_vals(self, write_off_line_vals=None):
        """docstring for _prepare_move_line_default_vals"""
        res = super(AccountPayment, self)._prepare_move_line_default_vals(write_off_line_vals)
        self.compute_taxes()
        for tax in self.tax_line_ids:
            date = self.date
            tax_ml_credit, tax_ml_dedit = self.get_tax_ml_val(tax, date)
            res += [tax_ml_credit]
            res += [tax_ml_dedit]
        return res

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        res.compute_taxes()
        return res

    def write(self, vals):
        res = super(AccountPayment, self).write(vals)
        for rec in self:
            if not 'tax_line_ids' in vals and not rec.tax_line_ids:
                rec.compute_taxes()
        return res

    def compute_taxes(self):
        """Function used in other module to compute the taxes on a fresh invoice created (onchanges did not applied)"""
        account_tax_line = self.env['account.tax.line']
        ctx = dict(self._context)
        for payment in self:
            # Delete non-manual tax lines
            self._cr.execute("DELETE FROM account_tax_line WHERE payment_tax_id=%s AND manual is False", (payment.id,))
#             self.invalidate_cache()

            # Generate one tax line per tax, however many petty lines it's applied to
            tax_grouped = payment.get_taxes_values()

            # Create new tax lines
            for tax in tax_grouped.values():
                account_tax_line.create(tax)

        # dummy write on self to trigger recomputations
        return self.with_context(ctx).write({'tax_line_ids': []})

    def get_taxes_values(self):
        tax_grouped = {}
        company = self.env.company
        for line in self.invoice_line:
            bill = line.invoice_id
            if bill.amount_suspend_vat != 0:
                for tax_line in bill.tax_line_ids:
#                     if tax_line.tax_line_id.use_suspend_vat and not tax_line.tax_line_id.tax_suspend_id.use_suspend_vat:
#                         continue
                    tax_suspend = tax_line.tax_id.tax_suspend_id
                    val = self._prepare_tax_line_vals(line, tax_line, tax_suspend)
                    key = self.env['account.tax.line'].get_grouping_key(val)
                    #add key group by inoice ref
                    vat_ref = self.name
                    if vat_ref:
                        key = self.env['account.tax.line'].add_invoice_ref_key(vat_ref, key)

                    if key not in tax_grouped:
                        tax_grouped[key] = val
                    else:
                        tax_grouped[key]['amount'] += val['amount']
                        tax_grouped[key]['base'] += val['base']
            else:
                for iv_line in bill.line_ids:
                    if iv_line.tax_ids and iv_line.tax_ids[0].PP36 and iv_line.tax_ids[0].use_suspend_vat:
                        tax_line = iv_line.tax_ids[0]
                        tax_suspend = tax_line.tax_suspend_id
                        val = self._prepare_tax_36_vals(iv_line, tax_line, tax_suspend)
                        key = self.env['account.tax.line'].get_grouping_key(val)
                        #add key group by inoice ref
                        if self.vat_ref:
                            vat_ref = self.vat_ref
                        elif self.payment_type == 'inbound':
                            vat_ref = self.name
                        else:
                            vat_ref = ''
#                         vat_ref = None
                        if vat_ref:
                            key = self.env['account.tax.line'].add_invoice_ref_key(vat_ref, key)

                        if key not in tax_grouped:
                            tax_grouped[key] = val
                        else:
                            tax_grouped[key]['amount'] += val['amount']
                            tax_grouped[key]['base'] += val['base']
        return tax_grouped

    def _prepare_tax_36_vals(self, line, tax, tax_suspend):
        date = self.date
        if self.payment_type == 'inbound':
            vat_ref = self.name
        else:
            vat_ref = ''
        company = self.company_id
        currency_unit =  self.currency_id._convert(line.price_unit, company.currency_id, company, date)
        taxes_res = tax_suspend.compute_all(
            currency_unit,
            quantity=line.quantity,
            currency=line.currency_id,
            product=line.product_id,
            partner=line.partner_id,
        )
        tax_amt = taxes_res['taxes'][0]['amount']
        tax_base = taxes_res['taxes'][0]['base']
        vals = {
            'payment_tax_id': self.id,
            'res_model': 'account.payment',
            'res_id': self.id,
            'name': tax.name,
            'tax_bill_id': tax.id,
            'tax_id': tax_suspend.id,
            'amount': round((tax_amt), 2),
            'base': round(tax_base, 2),
            'vat_ref': vat_ref,
            'manual': False,
            'account_id': tax_suspend.get_tax_tax(),
            'partner_id': self.partner_id.id or None,
            'month_vat': str(date.month),
            'year': str(date.year),
            'date': date,
        }
        return vals

    def _prepare_tax_line_vals(self, line, tax, tax_suspend):
        date = self.date
        if self.vat_ref:
            vat_ref = self.vat_ref
        elif self.payment_type == 'inbound':
            vat_ref = self.name
        else:
            vat_ref = ''
        vals = {
            'payment_tax_id': self.id,
            'res_model': 'account.payment',
            'res_id': self.id,
            'name': tax.name,
            'tax_bill_id': tax.tax_id.id,
            'tax_id': tax_suspend.id,
            'amount': round(tax.amount, 2),
            'base': tax.base,
            'vat_ref': vat_ref,
            'manual': False,
            'account_id': tax_suspend.get_tax_tax(),
            'partner_id': self.partner_id.id or None,
            'month_vat': str(date.month),
            'year': str(date.year),
            'date': date,
        }
        return vals

