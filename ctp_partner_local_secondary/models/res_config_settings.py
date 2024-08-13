# -*- coding: utf-8 -*-
import re
from odoo import api, fields, models 

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    second_local = fields.Char(string='Partner Secondary Language', default="Local")
    
    def modify_view(self):
        second_local = self.env['ir.config_parameter'].sudo().get_param('second_local', default="Local")
        view_partner_id = self.env.ref('ctp_partner_local_secondary.view_form_res_partner_inherit')
        view_company_id = self.env.ref('ctp_partner_local_secondary.view_form_res_company_inherit')
        view_partner_id.arch_base = re.sub('in \w+"', "in " + (second_local or "Local") + '"', view_partner_id.arch_base)
        view_company_id.arch_base = re.sub('in \w+"', "in " + (second_local or "Local") + '"', view_company_id.arch_base)

    @api.model
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('second_local', self.second_local)
        self.modify_view()

    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res['second_local'] = self.env['ir.config_parameter'].sudo().get_param('second_local', default="Local")
        return res
