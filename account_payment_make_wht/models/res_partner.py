
# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class ResPart(models.Model):
    _inherit = 'res.partner'

    building = fields.Char(
        string='Building',
    )
    
    floor = fields.Char(
        string='Floor',
    )
    
    room_no = fields.Char(
        string='Room Number',
    )    
    house_no = fields.Char(
        string='House No.',
    )

    
