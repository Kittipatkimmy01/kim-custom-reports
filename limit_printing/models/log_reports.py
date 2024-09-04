from odoo import models, fields, api


class LogReports(models.Model):
    _name = 'log.reports'

    name = fields.Char('Report Name')
    user_id = fields.Many2one('res.users', string='Printing By')
    date_print = fields.Datetime('Date Print')
    action_id = fields.Integer('Action Print ID', default=0)
    print_count = fields.Integer('Print Count', default=0, readonly=True)
    count = fields.Integer('Count', default=0, readonly=True, compute='_compute_print_count')
    ir_report_id = fields.Many2one('log.reports', 'Ir Actions Report')

    @api.depends('print_count', 'action_id')
    def _compute_print_count(self):
        for rec in self:
            if rec.action_id:
                check_action = self.search([('action_id', '=', rec.action_id)])
                total_print_count = sum(check_action.mapped('print_count'))

                rec.count = total_print_count
