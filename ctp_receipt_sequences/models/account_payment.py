from odoo import _, fields, models

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    def action_post(self):
        res = super().action_post()
        for rec in self:
            for line in rec.invoice_line:
                line.invoice_id.gen_seq_receipt()
        return res