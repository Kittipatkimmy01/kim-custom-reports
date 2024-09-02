from odoo import models, fields, api


class MasterPlan(models.Model):
    _name = 'master.plan'

    name = fields.Char(string='Name')
    plan_code = fields.Char(string='Plan Code')
    plan_cate = fields.Many2one('plan.category', string='Plan Category')
    description = fields.Html(string="Description")
    master_test_ids = fields.One2many(comodel_name='master.test.line', inverse_name='master_plan_id',
                                      string="Master Test", store=True,
                                      copy=False, auto_join=True)

    _sql_constraints = [
        ('plan_code', 'unique(plan_code)', 'This plan code has already been used.'),
    ]