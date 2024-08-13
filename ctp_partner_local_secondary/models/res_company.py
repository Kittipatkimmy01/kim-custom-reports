# -*- coding: utf-8 -*-
from odoo import api, fields, models

class ResCompany(models.Model):
    _inherit = 'res.company'

    local_name = fields.Char(related="partner_id.local_name", inverse="_inverse_local_name", store=True)
    local_street = fields.Char(related="partner_id.local_street", inverse="_inverse_local_street", store=True)
    local_street2 = fields.Char(related="partner_id.local_street2", inverse="_inverse_local_street2", store=True)
    local_city = fields.Char(related="partner_id.local_city", inverse="_inverse_local_city", store=True)
    local_state = fields.Char(related="partner_id.local_state", inverse="_inverse_local_state", store=True)
    local_zip = fields.Char(related="zip")
    local_country = fields.Char(related="partner_id.local_country", inverse="_inverse_local_country", store=True)
    
    def _inverse_local_name(self):
        for company in self:
            company.partner_id.local_name = company.local_name
    
    def _inverse_local_street(self):
        for company in self:
            company.partner_id.local_street = company.local_street
    
    def _inverse_local_street2(self):
        for company in self:
            company.partner_id.local_street2 = company.local_street2
    
    def _inverse_local_city(self):
        for company in self:
            company.partner_id.local_city = company.local_city
    
    def _inverse_local_state(self):
        for company in self:
            company.partner_id.local_state = company.local_state
    
    def _inverse_local_country(self):
        for company in self:
            company.partner_id.local_country = company.local_country
            