# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    pnd54 = fields.Boolean(
        string='PND54',
        store=True,
        compute='_compute_pnd_54',
    )
    move_pnd54_id = fields.Many2one(
        comodel_name='account.move',
        string='Move PDN54 Clear',
    )
    pnd54_state = fields.Selection(
        selection=[
            ('none', 'None'),
            ('not_clear', 'Not Clear'),
            ('cleared', 'Cleared'),
        ],
        compute='_compute_state_pnd54',
        store=True,
        string='State PND54 Clear',
    )

    @api.depends('partner_id', 'partner_id.wht_kind')
    def _compute_pnd_54(self):
        """docstring for _compute_pnd_54"""
        for rec in self:
            pnd54 = False
            if rec.payment_type == 'outbound':
                if rec.partner_id and rec.partner_id.wht_kind and rec.partner_id.wht_kind == 'pp54':
                    pnd54 = True
            rec.pnd54 = pnd54

    @api.depends('pnd54', 'state', 'move_pnd54_id', 'move_pnd54_id.state')
    def _compute_state_pnd54(self):
        """docstring for _compute_state_pnd54"""
        for rec in self:
            pnd54_state = 'none'
            if rec.pnd54 and rec.state == 'posted':
                if rec.move_pnd54_id and rec.move_pnd54_id.state == 'posted':
                    pnd54_state = 'cleared'
                else:
                    pnd54_state = 'not_clear'
            rec.pnd54_state = pnd54_state

    def button_open_journal_entry(self):
        obj_search = self
        action = {
            'name': _("Journal Entry"),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'context': {'create': False},
            'view_mode': 'tree,form',
        }
        obj_list_id = []
        if self.move_id:
            obj_list_id.append(self.move_id.id)
        if self.move_pnd54_id:
            obj_list_id.append(self.move_pnd54_id.id)
        action['domain'] = [('id', 'in', obj_list_id)]
        return action

    def clear_pnd54(self):
        """docstring for clear_pnd54"""
        if self.move_pnd54_id:
            return {
                'name': _("Journal Entry"),
                'type': 'ir.actions.act_window',
                'res_model': 'account.move',
                'context': {'create': False},
                'view_mode': 'form',
                'res_id': self.move_pnd54_id.id,
            }
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'wizard.clear.pnd54',
            'view_mode': 'form',
            'target': 'new',
        }

    def get_pnd54_vat_move_line(self, date, journal):
        partner = None
        partner = self.partner_id
        company = self.company_id
        acc_pnd54_ap = company.acc_pnd54_ap_id.id
        currency_total =  self.currency_id._convert(self.invoice_total, company.currency_id, company, date)
        rate = partner.rate_54
        amt = (currency_total / 100) * rate
        aml = []
        aml.append((0, 0, {
            'name': 'PND54(AP)',
            'debit': amt,
            'credit' : 0,
            'account_id' : acc_pnd54_ap,
            'partner_id': partner.id,
            'date': date,
        }))
        aml.append((0, 0, {
            'name' : journal.name,
            'debit' : 0,
            'credit' : amt,
            'account_id' : journal.default_account_id.id,
            'partner_id' : partner.id,
            'date' :  date,
        }))
        return aml

    def get_pnd54_move_reverse(self, date, ref, wiz):
        journal = wiz.journal_id
        company_id = self.env.company
        move_line = self.get_pnd54_vat_move_line(date=date, journal=journal)
        move_val = {
            'date': date,
            'ref': ref or '',
            'company_id': company_id.id,
            'journal_id': journal.id,
            'move_type': 'entry',
            'line_ids': move_line,
        }
        return move_val

    def create_move_pnd54(self, wiz):
        """docstring for create_move_pnd54"""
        date = wiz.date
        ref = self.name
        move_rpv = self.env['account.move'].create(self.get_pnd54_move_reverse(date, ref, wiz))
        self.write({'move_pnd54_id': move_rpv.id})
        move_rpv.action_post()
        return True

    def _prepare_move_line_default_vals(self, write_off_line_vals=None):
        res = super(AccountPayment, self)._prepare_move_line_default_vals(write_off_line_vals)
        if self.pnd54:
            currency_id = self.currency_id.id
            company = self.company_id
            currency_total =  self.currency_id._convert(self.invoice_total, company.currency_id, company, self.date)
            rate = self.partner_id.rate_54
            amt = (currency_total / 100) * rate
            acc_pnd54_ext = company.acc_pnd54_ext_id.id
            acc_pnd54_ap = company.acc_pnd54_ap_id.id
            line_vals = []
            line_vals += [{
                'name': "PND54 EXT",
                'date_maturity': self.date,
                'amount_currency': amt,
                'currency_id': currency_id,
                'debit': amt,
                'credit': 0.0,
                'account_id': acc_pnd54_ext,
                'partner_id': self.partner_id.id,
            }]
            line_vals += [{
                'name': "PND54 AP",
                'date_maturity': self.date,
                'amount_currency': -amt,
                'currency_id': currency_id,
                'credit': amt,
                'debit': 0.0,
                'account_id': acc_pnd54_ap,
                'partner_id': self.partner_id.id,
            }]
            res += line_vals
        return res
