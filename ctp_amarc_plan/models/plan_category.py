from odoo import models, fields


class PlanCategory(models.Model):
    _name = 'plan.category'

    name = fields.Char(string='Name')
