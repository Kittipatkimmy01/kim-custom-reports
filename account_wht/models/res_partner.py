# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class Partner(models.Model):
    _inherit = 'res.partner'

    wht_kind =  fields.Selection(
        [
            ('pp4','(4) PND3'),
            ('pp7','(7) PND53'),
            ('pp54','PND54'),
        ],
        string = 'Type',
        required = False
    )
    rate_54 = fields.Float(
        string='Rate PND54',
    )

    @api.onchange('company_type', 'country_id')
    def onchange_company_type_wht(self):
        for rec in self:
            if rec.parent_id:
                rec.wht_kind = rec.parent_id.wht_kind
            elif rec.company_type == 'person':
                rec.wht_kind = 'pp4'
            elif rec.company_type == 'company':
                if rec.country_id.name == 'Thailand':
                    rec.wht_kind = 'pp7'
                else:
                    rec.wht_kind = 'pp54'

