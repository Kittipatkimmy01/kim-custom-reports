# -*- coding: utf-8 -*-
from odoo import api, fields, models

ADDRESS_LOCAL_FIELDS = ('local_street', 'local_street2', 'local_city', 'local_state', 'local_country')

class ResPartner(models.Model):
    _inherit = 'res.partner'

    local_name = fields.Char()
    local_street = fields.Char()
    local_street2 = fields.Char()
    local_city = fields.Char()
    local_state = fields.Char()
    local_zip = fields.Char(related="zip")
    local_country = fields.Char()
    contact_just_address = fields.Char(compute='_compute_contact_just_address', string='Complete Address')
    contact_local_address = fields.Char(compute='_compute_contact_local_address', string='Complete Local Address')
    contact_local_just_address = fields.Char(compute='_compute_contact_local_just_address', string='Complete Local Address')
    
    def write(self, vals):
        try:
            address_local_fields = self._address_local_fields()
            if self.is_company:
                addr_vals = {key: vals.get(key) for key in address_local_fields if key in vals  and (vals.get(key) or vals.get(key) is False)}
                if addr_vals:
                    is_company_id = self.id
                    contact_partners = self.env['res.partner'].search([('parent_id', '=', is_company_id), ('type', '=', 'contact')])
                    for contact in contact_partners:
                        super(ResPartner, contact).write(addr_vals)
            elif self.parent_id and self.type == 'contact':
                for key in address_local_fields:
                    vals[key] = self.parent_id[key]
            return super(ResPartner, self).write(vals)
        except:
            return True
        
    @api.model
    def _address_local_fields(self):
        return list(ADDRESS_LOCAL_FIELDS)

    @api.onchange('parent_id')
    def onchange_local_parent_id(self):
        if self.type == 'contact':
            for key in self._address_local_fields():
                self[key] = self.parent_id[key]
        return
    
    @api.depends(lambda self: self._display_address_depends())
    def _compute_contact_just_address(self):
        for partner in self:
            partner.contact_just_address = partner._display_just_address()
            
    def _display_just_address(self, without_company=False):
        address_format, args = self._prepare_display_just_address(without_company)
        return address_format % args

    def _prepare_display_just_address(self, without_company=False):
        address_format = self._get_address_format()
        args = {
            'state_code': self.state_id.code or '',
            'state_name': self.state_id.name or '',
            'country_code': self.country_id.code or '',
            'country_name': self._get_country_name(),
            'company_name': self.commercial_company_name or '',
        }
        for field in self._formatting_address_fields():
            args[field] = getattr(self, field) or ''
        if without_company:
            args['company_name'] = ''
        return address_format, args
            
    @api.depends(lambda self: self._display_address_depends())
    def _compute_contact_local_address(self):
        for partner in self:
            partner.contact_local_address = partner._display_local_address()
            
    def _display_local_address(self, without_company=False):
        address_format, args = self._prepare_display_local_address(without_company)
        return address_format % args

    def _prepare_display_local_address(self, without_company=False):
        address_format = self._get_address_format()
        args = {
            'zip': self.zip or '',
        }
        for field in self._formatting_address_fields():
            args[field] = getattr(self, field) or ''
        if without_company:
            args['company_name'] = ''
        elif self.commercial_company_name:
            address_format = '%(company_name)s \n' + address_format
        args['street'] = self.local_street if self.local_street else ''
        args['street2'] = self.local_street2 if self.local_street2 else ''
        args['city'] = self.local_city if self.local_city else ''
        args['state_name'] = self.local_state if self.local_state else ''
        args['country_name'] = self.local_country if self.local_country else ''
        args['company_name'] = '' if without_company else self.parent_id.local_name
        return address_format, args
    
    @api.depends(lambda self: self._display_address_depends())
    def _compute_contact_local_just_address(self):
        for partner in self:
            partner.contact_local_just_address = partner._display_local_just_address()
            
    def _display_local_just_address(self, without_company=False):
        address_format, args = self._prepare_display_local_just_address(without_company)
        return address_format % args

    def _prepare_display_local_just_address(self, without_company=False):
        address_format = self._get_address_format()
        args = {
            'zip': self.zip or '',
        }
        for field in self._formatting_address_fields():
            args[field] = getattr(self, field) or ''
        if without_company:
            args['company_name'] = ''
        args['street'] = self.local_street if self.local_street else ''
        args['street2'] = self.local_street2 if self.local_street2 else ''
        args['city'] = self.local_city if self.local_city else ''
        args['state_name'] = self.local_state if self.local_state else ''
        args['country_name'] = self.local_country if self.local_country else ''
        args['company_name'] = '' if without_company else self.parent_id.local_name
        return address_format, args