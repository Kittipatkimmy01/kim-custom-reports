from odoo import _, fields, models

class AccountMove(models.Model):
    _inherit = "account.move"

    receipt_sequences = fields.Char(string="Receipt Sequences", default="Waiting", readonly=False, tracking=True)

    def gen_seq_receipt(self):
        """docstring for gen_seq_receipt"""
        for rec in self:
            if rec.move_type == "out_invoice":
                if rec.receipt_sequences == "Waiting":
                    rec.receipt_sequences = self.env["ir.sequence"].next_by_code("seq.receiptref.inv")

    """ @api.model
    def write(self, vals):
        for rec in self:
            _logger.warning("rec: %s", rec)
            move = self.env["account.move"].search([("name", "=", rec.ref)])
            _logger.warning("move: %s", move)
            if move:
                if move.move_type == "out_invoice" and move.payment_state in ("in_payment", "paid", "partial"):
                    if move.receipt_sequences == "Waiting":
                        receiptref = self.env["ir.sequence"].next_by_code("seq.receiptref.inv")
                        self.env["account.move"].search([("name", "=", rec.ref)]).write({"receipt_sequences": receiptref})
            return super(AccountMove, self).write(vals) """