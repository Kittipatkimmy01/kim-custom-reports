# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class WizardClearPND54(models.TransientModel):
    _name = 'wizard.clear.pnd54'
    _description = 'Clear PND 54'

    payment_id = fields.Many2one(
        comodel_name='account.payment',
        string='Payment',
    )
    journal_id = fields.Many2one(
        comodel_name='account.journal',
        string='Journal',
        domain="[('type', 'in', ('bank','cash'))]",
    )
    date = fields.Date(
        string='Date',
    )

    api.model
    def default_get(self, fields):
        res = super(WizardClearPND54, self).default_get(fields)
        context = self._context
        if context.get('active_id'):
            payment_id = context.get('active_id')
            res.update({
                'payment_id': payment_id
            })
        return res

    def clear_54(self):
        """docstring for clear_54"""
        payment = self.payment_id
        wiz = self
        payment.create_move_pnd54(wiz)
        return
