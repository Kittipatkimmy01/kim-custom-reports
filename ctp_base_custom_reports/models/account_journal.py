from odoo import models, fields


class AccountJournal(models.Model):
    _inherit = "account.journal"

    voucher_title_general = fields.Char("Voucher Title(General)")
    voucher_title_general_th = fields.Char("Voucher Title(General)(TH)")
    voucher_title_receive = fields.Char("Voucher Title(Receive)")
    voucher_title_receive_th = fields.Char("Voucher Title(Receive)(TH)")
    voucher_title_pay = fields.Char("Voucher Title(Pay)")
    voucher_title_pay_th = fields.Char("Voucher Title(Pay)(TH)")
