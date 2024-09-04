from odoo import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    state_print_ids = fields.Many2many('state.for.print', string='Status Print',
                                       compute='_compute_state_print')

    def _compute_state_print(self):
        for rec in self:
            action_report = self.env['actions.report'].search([('action_id', '=', rec.id)])
            state_ids = []

            if action_report:
                get_status = self.env['state.for.print'].search([('name', '=', 'Order')])
                state_ids.extend(get_status.ids)

            if rec.picking_ids:
                for picking in rec.picking_ids:
                    picking_report = self.env['actions.report'].search([('action_id', '=', picking.id)])
                    if picking_report:
                        get_status = self.env['state.for.print'].search([('name', '=', 'Picking')])
                        state_ids.extend(get_status.ids)

            if rec.invoice_ids:
                for invoice in rec.invoice_ids:
                    invoice_report = self.env['actions.report'].search([('action_id', '=', invoice.id)])
                    get_payment = self.env['account.payment'].browse(invoice.id)
                    payment_report = self.env['actions.report'].search([('action_id', '=', get_payment.id)])

                    if invoice_report:
                        get_status = self.env['state.for.print'].search([('name', '=', 'Invoice')])
                        state_ids.extend(get_status.ids)

                    if payment_report:
                        get_status = self.env['state.for.print'].search([('name', '=', 'Payment')])
                        state_ids.extend(get_status.ids)

            rec.state_print_ids = state_ids

    def get_approve_request(self):
        for rec in self:
            approve = self.env['approval.request'].search([('sale_order_id', '=', rec.id)])
            if approve:
                rec.approve_request_ids = approve.ids
            else:
                rec.approve_request_ids = False

    approve_request_ids = fields.Many2many('approval.request', default=get_approve_request)
    approve_request_count = fields.Integer(compute='_compute_approve_request_count', default=0)

    def _compute_approve_request_count(self):
        for rec in self:
            if rec.approve_request_ids:
                rec.approve_request_count = int(len(rec.approve_request_ids.ids))
            else:
                rec.approve_request_count = 0

    def action_view_request_approve(self):
        action = {
            'res_model': 'approval.request',
            'type': 'ir.actions.act_window',
        }
        if len(self.approve_request_ids.ids) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': self.approve_request_ids.ids[0],
            })
        else:
            action.update({
                'name': _("Request Approve Limit Printing For %s", self.name),
                'domain': [('id', 'in', self.approve_request_ids.ids)],
                'view_mode': 'tree,form',
            })

        return action
