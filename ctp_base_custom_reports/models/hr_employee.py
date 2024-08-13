from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    signature = fields.Binary(string="Sinature")
    user_signature = fields.Binary(string="User Sinature")
