# -*- coding: utf-8 -*-

from odoo import models, api, fields
from datetime import datetime
from dateutil import relativedelta


class ProductTemplate(models.Model):
    _inherit = "product.template"

    second_uom_id = fields.Many2one('uom.uom', string="2nd Unit of Measure")
    second_uom_po_id = fields.Many2one('uom.uom', string="2nd Purchase UoM")
    is_active_2nd_uom = fields.Boolean(string='Active 2nd UoM',default=True,)
    enpro = fields.Boolean(
        string='Enpro',
        default=False,
    )

#     property_account_income_id = fields.Many2one(
#         domain="['&', '&', '&', ('deprecated', '=', False), ('account_type', 'not in', ('asset_receivable','liability_payable','asset_cash','liability_credit_card', 'asset_cash')), ('company_id', '=', current_company_id), ('is_off_balance', '=', False)]"
#     )

    def _inactive_product(self):
        for rec in self:
            if rec.enpro:
                mo = datetime.today() - relativedelta.relativedelta(months=3)
                create = rec.write_date
                if create < mo:
                    rec.update({'active': False})
