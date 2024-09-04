from odoo import models, fields, api, _
from datetime import datetime


class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    limit_printing = fields.Integer('Limit Printing', default=0)
    count = fields.Integer('Log Count', default=0, store=True)
    log_report_id = fields.One2many('log.reports', 'ir_report_id')
    print_count = fields.Integer(compute='_compute_print_count')
    print_option = fields.Selection(selection=[
        ('print', 'Print'),
        ('download', 'Download'),
        ('open', 'Open')
    ], default='print', string='Default Printing Option')
    default_print_option = fields.Selection(selection=[
        ('print', 'Print'),
        ('download', 'Download'),
        ('open', 'Open')
    ], default='download', string='Default Printing Option', compute='_compute_default_print_option')
    access_right_id = fields.Char('Access Right For Approve', compute='_compute_access_right')
    state = fields.Char(compute='_compute_get_state')

    def _compute_access_right(self):
        uid = self.env.context.get('uid')
        search_users = self.env['res.users'].browse(uid)
        if search_users:
            is_approved_user = False
            is_approved_manager = False
            for group in search_users.groups_id:
                if group.name == 'Approved Printing User':
                    is_approved_user = True
                if group.name == 'Approved Printing Manager':
                    is_approved_manager = True

            if is_approved_manager:
                self.access_right_id = 'access_approved_manager'
            elif is_approved_user:
                self.access_right_id = 'access_approved_user'
            else:
                self.access_right_id = ''

    def _compute_get_state(self):
        model = self.env.context.get('active_model')
        get_model = self.env[model].browse(self.env.context.get('active_id'))
        if get_model:
            self.state = get_model.state
        else:
            self.state = ''

    @api.depends('default_print_option')
    def _compute_default_print_option(self):
        for rec in self:
            if rec.default_print_option != 'download':
                rec.default_print_option = 'download'

    def _compute_print_count(self):
        active = self.env.context.get('active_id')
        actions_report = self.env['actions.report'].search([('action_id', '=', active)], limit=1)
        for rec in self:
            rec.print_count = actions_report.print_count

    def _render_qweb_pdf_prepare_streams(self, report_ref, data, res_ids=None):
        res = super(IrActionsReport, self)._render_qweb_pdf_prepare_streams(report_ref, data, res_ids=res_ids)
        check_report = self.env['actions.report'].search([('name', '=', report_ref), ('action_id', '=', res_ids)])
        get_log = self.env['log.reports']
        get_report = self._get_report(report_ref)
        model = get_report.model_id.model
        # search_model = self.env[model].search([('id', '=', res_ids[0])])

        get_log.create({
            'name': str(report_ref),
            'action_id': res_ids[0],
            'user_id': get_report.model_id.env.uid,
            'print_count': 1,
            'date_print': datetime.now()
        })
        get_report.count += 1

        if not check_report:
            check_report.create({
                'name': str(report_ref),
                'action_id': res_ids[0],
                # 'report_order': search_model.name,
                'user_id': get_report.model_id.env.uid,
                'print_count': 1,
                'date_print': datetime.now()
            })
        else:
            check_report.write({
                'user_id': get_report.model_id.env.uid,
                'print_count': check_report.print_count + 1,
                'date_print': datetime.now()
            })

        return res

    def view_log_reports(self):
        action = self.env['ir.actions.actions']._for_xml_id('limit_printing.log_reports_action')
        action['context'] = {'name': self.report_name, 'search_default_name': self.report_name}
        return action

    def _get_readable_fields(self):
        data = super()._get_readable_fields()
        data |= {'limit_printing', 'print_count', 'print_option', 'access_right_id', 'print_report_name',
                 'state'}
        return data

    def report_action(self, docids, data=None, config=True):
        data = super(IrActionsReport, self).report_action(docids, data, config)
        data.update({'id': self.id, 'limit_printing': self.limit_printing, 'print_count': self.print_count,
                     'print_option': self.print_option, 'access_right_id': self.access_right_id,
                     'state': self.state})
        return data

    # def reset_print_count(self):
    #     actions_report = self.env['actions.report'].search([('action_id', '=', self.id)])
    #     if actions_report:
    #         actions_report.write({
    #             'print_count': 0,
    #         })
    #
    #     return True
