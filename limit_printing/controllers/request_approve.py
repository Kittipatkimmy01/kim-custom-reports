from odoo import http, _


class RequestApproveController(http.Controller):

    @http.route('/request_to_approve', auth='public', type='json')
    def request_to_approve(self, **kwargs):
        approver = http.request.env['approval.category'].search([('is_limit_printing', '=', True)])
        if approver:
            for approve in approver:
                active_model = kwargs.get('args')[1]['additionalContext']['active_model']
                active = kwargs.get('args')[1]['additionalContext']['active_id']
                action_report = http.request.env['actions.report'].search([('action_id', '=', active)])
                model = http.request.env[active_model].browse(active)
                name_order = model.name
                user_id = kwargs.get('args')[0]

                approve_request = http.request.env['approval.request'].create({
                    'name': '%s (%s)' % (approve.name, name_order),
                    'request_owner_id': user_id,
                    'category_id': approve.id,
                    'is_limit_printing': True,
                    'request_status': 'new',
                    'reference': name_order,
                    'action_id': action_report.id,
                })
                if active_model == 'sale.order':
                    sale = http.request.env['sale.order'].browse(active)
                    approve_request.write({
                        'sale_order_id': sale.id,
                    })

                if active_model == 'purchase.order':
                    po = http.request.env['purchase.order'].browse(active)
                    approve_request.write({
                        'purchase_order_id': po.id,
                    })

                if approve_request.sale_order_id:
                    sale.sudo().write({
                        'approve_request_ids': [(4, approve_request.id)]
                    })
                if approve_request.purchase_order_id:
                    po.sudo().write({
                        'approve_request_ids': [(4, approve_request.id)]
                    })

        return True

        # action = {
        #     'res_model': 'approval.request',
        #     'type': 'ir.actions.act_window',
        #     'view_mode': 'form',
        #     'context': {
        #         'default_name': '%s (%s)' % (approve.name, name_order),
        #         'default_category_id': approve.id,
        #         'default_request_owner_id': user_id,
        #         'default_request_status': 'new',
        #         'default_reference': name_order,
        #         'default_is_limit_printing': True,
        #     }
        # }
