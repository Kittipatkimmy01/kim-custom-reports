# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class AccountTaxLine(models.Model):
    _inherit = 'account.tax.line'

    move_tax_id = fields.Many2one(
        'account.move',
        string='Account Move',
        ondelete='cascade',
        index=True
    )

    def map_tax(self, tax_grouped):
        tax_grouped = super().map_tax(tax_grouped)
        for petty in self.mapped('move_tax_id'):
            tax_grouped[petty.id] = petty.get_taxes_values()
        return tax_grouped

    def check_tax(self, tax, tax_grouped, key):
        tax_base = super().check_tax(tax, tax_grouped, key)
#         tax_base = 0.0
        if tax.move_tax_id and key in tax_grouped[tax.move_tax_id.id]:
            tax_base = tax_grouped[tax.move_tax_id.id][key]['base']
        """Hook for check other invoice tax"""
        return tax_base

class AccountMove(models.Model):
    _inherit = 'account.move'

    def _compute_amount_suspend_vat(self):
        for invoice in self:
            amount = 0
            for line in invoice.tax_line_ids:
                if line.tax_id and line.tax_id.use_suspend_vat:
                    amount += line.amount
            invoice.amount_suspend_vat = amount

    tax_line_ids = fields.One2many(
        comodel_name='account.tax.line',
        inverse_name='move_tax_id',
        string='Tax Lines',
        copy=False
    )
    amount_suspend_vat = fields.Monetary(
        string = 'Amount Suspend Vat',
        compute = '_compute_amount_suspend_vat',
    )
    vat_ref = fields.Char(
        string='Vat Reference',
    )

    def write(self, vals):
        res = super().write(vals)
        for rec in self:
            if not 'tax_line_ids' in vals and not rec.tax_line_ids:
                rec.compute_taxes()
        return res

    def action_post(self):
        res = super().action_post()
        for rec in self:
            for line in rec.tax_line_ids:
                if (rec.move_type == 'out_invoice' and line.tax_id.auto_usevat_so) or\
                    (rec.move_type == 'in_invoice' and line.tax_id.auto_usevat_po):
                    line.verify_tax()
        return res

    def button_draft(self):
        for tax in self.tax_line_ids:
            tax.unverify_tax()
        res = super().button_draft()
        return res

    def compute_taxes(self):
        """Function used in other module to compute the taxes on a fresh invoice created (onchanges did not applied)"""
        account_tax_line = self.env['account.tax.line']
        ctx = dict(self._context)
        for move in self:
            # Delete non-manual tax lines
            self._cr.execute("DELETE FROM account_tax_line WHERE move_tax_id=%s AND manual is False", (move.id,))
#             self.invalidate_cache()

            # Generate one tax line per tax, however many petty lines it's applied to
            tax_grouped = move.get_taxes_values()

            # Create new tax lines
            for tax in tax_grouped.values():
                account_tax_line.create(tax)

        # dummy write on self to trigger recomputations
        return self.with_context(ctx).write({'tax_line_ids': []})

    def get_taxes_values(self):
        tax_grouped = {}
        company = self.env.company
        for line in self.line_ids:
            if line.tax_line_id:
                tax_line = line.tax_line_id
                val = self._prepare_tax_line_vals(line, tax_line)
                key = self.env['account.tax.line'].get_grouping_key(val)
                #add key group by inoice ref
                if self.move_type == 'out_invoice':
                    vat_ref = self.name
                elif self.move_type == 'in_invoice':
                    vat_ref = self.ref
                else:
                    vat_ref = ''
                if vat_ref:
                    key = self.env['account.tax.line'].add_invoice_ref_key(vat_ref, key)

                if key not in tax_grouped:
                    tax_grouped[key] = val
                else:
                    tax_grouped[key]['amount'] += val['amount']
                    tax_grouped[key]['base'] += val['base']
        return tax_grouped

    def _prepare_tax_line_vals(self, line, tax):
        date = self.invoice_date or fields.Datetime.now()
        if self.move_type == 'out_invoice':
            vat_ref = self.name
        elif self.move_type == 'in_invoice':
            vat_ref = self.ref
        else:
            vat_ref = ''
        vals = {
            'move_tax_id': self.id,
            'res_model': 'account.move',
            'res_id': self.id,
            'name': tax.name,
            'tax_id': tax.id,
            'amount': round(line.balance, 2),
            'base': line.tax_base_amount,
            'vat_ref': vat_ref,
            'manual': False,
            'account_id': tax.get_tax_tax(),
            'partner_id': self.partner_id.id,
            'month_vat': str(date.month),
            'year': str(date.year),
            'date': date,
        }
        return vals

