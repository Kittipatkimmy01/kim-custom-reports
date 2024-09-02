from odoo import models, fields, api


class MasterAnalyze(models.Model):
    _name = 'master.analyze'
    _rec_name = 'analyze_code'

    name = fields.Char(string='Name')
    analyze_code = fields.Char(string='Analyze Code')
    description = fields.Html(string="Description")
    use_for_bool = fields.Boolean(string='Use For')
    master_plan_id = fields.Many2one('master.plan', string='Plan')
    price = fields.Float(string='Price')
    uom_id = fields.Many2one(comodel_name='uom.uom', string="Unit")


class MasterAnalyzeLine(models.Model):
    _name = 'master.analyze.line'

    name = fields.Char(string='Name')
    analyze_code = fields.Char(string='Analyze Code')
    description = fields.Html(string="Description")
    use_for_bool = fields.Boolean(string='Use For')
    master_plan_id = fields.Many2one('master.plan', string='Plan')
    price = fields.Float(string='Price')
    master_analyze_id = fields.Many2one('master.analyze', string='Analyze Code')
    uom_id = fields.Many2one(comodel_name='uom.uom', string="Unit")

    master_test_id = fields.Many2one(
        comodel_name='master.test',
        string="Master Test", ondelete='cascade', index=True, copy=False)

    @api.onchange('master_analyze_id')
    def _compute_master_analyze(self):
        for rec in self:
            if rec.master_analyze_id:
                rec.name = rec.master_analyze_id.name or ''
                rec.description = rec.master_analyze_id.description or ''
                rec.master_plan_id = rec.master_analyze_id.master_plan_id.id or False
                rec.uom_id = rec.master_analyze_id.uom_id.id or False
