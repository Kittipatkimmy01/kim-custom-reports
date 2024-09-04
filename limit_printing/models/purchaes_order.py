from odoo import models, fields, api, _


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def get_approve_request(self):
        for rec in self:
            approve = self.env['approval.request'].search([('purchase_order_id', '=', rec.id)])
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