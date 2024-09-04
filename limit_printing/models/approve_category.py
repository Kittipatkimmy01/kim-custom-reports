from odoo import models, fields, _, api


class ApprovalCategory(models.Model):
    _inherit = 'approval.category'

    is_limit_printing = fields.Boolean('Limit Printing', default=False)

    def create_request(self):
        self.ensure_one()
        # If category uses sequence, set next sequence as name
        # (if not, set category name as default name).

        return {
            "type": "ir.actions.act_window",
            "res_model": "approval.request",
            "views": [[False, "form"]],
            "context": {
                'default_name': _('New') if self.automated_sequence else self.name,
                'default_category_id': self.id,
                'default_request_owner_id': self.env.user.id,
                'default_request_status': 'new',
                'default_is_limit_printing': self.is_limit_printing if self.is_limit_printing else False,

            },
        }


class ApprovalRequest(models.Model):
    _inherit = 'approval.request'

    sale_order_id = fields.Many2one('sale.order')
    purchase_order_id = fields.Many2one('purchase.order')
    is_limit_printing = fields.Boolean('Limit Printing', default=False)
    action_id = fields.Many2one('actions.report', 'Action Print Report')

    def action_approve(self, approver=None):
        res = super().action_approve()
        self._ensure_can_approve()

        if self.is_limit_printing and self.action_id:
            self.action_id.write({
                'print_count': 0,
            })

        if not isinstance(approver, models.BaseModel):
            approver = self.mapped('approver_ids').filtered(
                lambda approver: approver.user_id == self.env.user
            )
        approver.write({'status': 'approved'})
        self.sudo()._update_next_approvers('pending', approver, only_next_approver=True)
        self.sudo()._get_user_approval_activities(user=self.env.user).action_feedback()
        return res
