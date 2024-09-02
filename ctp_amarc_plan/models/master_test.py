from odoo import models, fields, api


class MasterTest(models.Model):
    _name = 'master.test'
    _rec_name = 'test_code'

    name = fields.Char(string='Name')
    test_code = fields.Char(string='Test Code')
    test_no_coa = fields.Char(string='Test No COA')
    method_id = fields.Many2one('method.config', string='Method')
    tm_id = fields.Many2one('tm.config', string='TM')
    description = fields.Html(string="Description")
    standard_unit = fields.Float(string='Standard Unit (mg/ml)')
    tat_standard_revise = fields.Char(string='TAT Standard (WD) Revise')
    tat_standard = fields.Char(string='TAT Standard')
    tat_express = fields.Char(string='TAT Express (WD)')
    sample_qty_minimum = fields.Float(string='Sample QTY Minimum (g/ml)')
    sample_qty_qty = fields.Float(string='Sample QTY Units (PacKage)')
    boi_selected = fields.Selection([('boi', 'BOI'), ('non', 'Non Boi')], string='BOI')
    product_id = fields.Many2one('product.product', string='Product')

    master_analyze_ids = fields.One2many(comodel_name='master.analyze.line', inverse_name='master_test_id',
                                         string="Master Analyze", copy=False, auto_join=True)

    _sql_constraints = [
        ('test_code', 'unique(test_code)', 'This test code has already been used.'),
    ]


class MasterTestLine(models.Model):
    _name = 'master.test.line'

    name = fields.Char(string='Name')
    test_code = fields.Char(string='Test Code')
    test_no_coa = fields.Char(string='Test No COA')
    method_id = fields.Many2one('method.config', string='Method')
    tm_id = fields.Many2one('tm.config', string='TM')
    description = fields.Html(string="Description")
    standard_unit = fields.Float(string='Standard Unit (mg/ml)')
    tat_standard_revise = fields.Char(string='TAT Standard (WD) Revise')
    tat_standard = fields.Char(string='TAT Standard')
    tat_express = fields.Char(string='TAT Express (WD)')
    sample_qty_minimum = fields.Float(string='Sample QTY Minimum (g/ml)')
    sample_qty_qty = fields.Float(string='Sample QTY Units (PacKage)')
    boi_selected = fields.Selection([('boi', 'BOI'), ('non', 'Non Boi')], string='BOI')
    product_id = fields.Many2one('product.product', string='Product')
    master_test_id = fields.Many2one('master.test', string='Test Code')

    master_plan_id = fields.Many2one(
        comodel_name='master.plan',
        string="Master Plan", ondelete='cascade', index=True, copy=False)

    @api.onchange('master_test_id')
    def _compute_master_test(self):
        for rec in self:
            if rec.master_test_id:
                rec.name = rec.master_test_id.name or ''
                rec.test_no_coa = rec.master_test_id.test_no_coa or ''
                rec.method_id = rec.master_test_id.method_id.id or False
                rec.tm_id = rec.master_test_id.tm_id.id or ''
                rec.description = rec.master_test_id.description or ''
                rec.standard_unit = rec.master_test_id.standard_unit or 0.0
                rec.tat_standard_revise = rec.master_test_id.tat_standard_revise or ''
                rec.tat_standard = rec.master_test_id.tat_standard or ''
                rec.tat_express = rec.master_test_id.tat_express or ''
                rec.sample_qty_minimum = rec.master_test_id.sample_qty_minimum or 0.0
                rec.sample_qty_qty = rec.master_test_id.sample_qty_qty or 0.0
                rec.boi_selected = rec.master_test_id.boi_selected or ''
                rec.product_id = rec.master_test_id.product_id.id or False
