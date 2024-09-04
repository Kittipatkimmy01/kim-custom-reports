from odoo import models, fields


class ActionsReport(models.Model):
    _name = 'actions.report'
    _rec_name = 'name'

    name = fields.Char('Report Name', required=True)
    action_id = fields.Integer('Action Print ID', default=0)
    user_id = fields.Many2one('res.users', 'Printing By')
    print_count = fields.Integer('Print Count', default=0, readonly=1)
    date_print = fields.Datetime('Date Print')
    report_order = fields.Char('Report Order')
