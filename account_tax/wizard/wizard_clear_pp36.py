# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class WizardClearPP36(models.TransientModel):
    _name = 'wizard.clear.pp36'
    _description = 'Clear PP 36'

    tax_line_id = fields.Many2one(
        comodel_name='account.tax.line',
        string='Tax Line',
    )
    journal_id = fields.Many2one(
        comodel_name='account.journal',
        string='Journal',
        domain="[('type', 'in', ('bank','cash'))]",
    )
    date = fields.Date(
        string='Date',
    )
    vat_ref = fields.Char(
        string='Vat Reference',
    )

    @api.model
    def default_get(self, fields):
        res = super(WizardClearPP36, self).default_get(fields)
        context = self._context
        if context.get('active_id'):
            tax_line_id = context.get('active_id')
            res.update({
                'tax_line_id': tax_line_id
            })
        return res

    def clear_36(self):
        """docstring for clear_36"""
        txl = self.tax_line_id
        txl.update({
            'vat_ref': self.vat_ref,
            'date': self.date,
            'year': str(self.date.year),
            'month_vat': str(self.date.month),
        })
        wiz = self
        txl.create_move_pp36(wiz)
        txl.update({'is_verify': True})
        return
