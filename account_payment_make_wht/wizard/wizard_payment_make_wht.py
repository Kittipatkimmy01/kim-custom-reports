# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError


class PaymentMakeWht(models.TransientModel):
    _name = "payment.make.wht"
    _description = "Payment Make WHT"

    date_doc =  fields.Date(
        'Document Date',
        default = fields.Datetime.now
    )
    wht_ids = fields.One2many(
        comodel_name='payment.make.wht.line',
        inverse_name='wht_payment_id',
        string='Line',
    )
    wht_payment = fields.Selection([
         ('pm1', '(1) With holding tax'),
         ('pm2', '(2) Forever'),
         ('pm3', '(3) Once'),
         ('pm4', '(4) Other'),
         ], 'WHT Payment',
       default = 'pm1',
       required=True
    )

    @api.model
    def default_get(self, fields):
        res = super(PaymentMakeWht, self).default_get(fields)
        active_id = self._context.get('active_id')
        payment_line = self.env['account.invoice.payment.line'].search([
            ('payment_id','=',active_id),
        ])
        payment = self.env[self._context.get('active_model')].browse([active_id])
        items = []
        for line in payment_line:
            if line.wht_total == 0:
                continue
            partner = payment.partner_id
            method = self.get_payment_method(partner, payment.payment_type)
            move = line.invoice_id
            for mline in move.line_ids:
                if mline.wht_type:
                    items.append((0, 0, {
                        'invoice_id': move.id,
                        'wht_kind': partner.wht_kind if partner.wht_kind else None,
                        'payment_method_id': method,
                        'wht_type': mline.wht_type.id,
                        'wht_base': mline.price_subtotal,
                        'total_wht': mline.total_wht,
                        'wht_rate': mline.wht_type.percentage,
                    }))
        res['wht_ids'] = items
        return res

    def get_payment_method(self, partner, payment_type):
        """docstring for get_payment_method"""
        method = False
        if partner.wht_kind == 'pp4' or partner.is_company is False:
            if payment_type in ('inbound','sale'):
                method = self.env.company.sale_method3_id.id
            else:
                method = self.env.company.payment_method3_id.id
        elif partner.wht_kind == 'pp7':
            if payment_type in ('inbound', 'sale'):
                method =  self.env.company.sale_method53_id.id
            else:
                method = self.env.company.payment_method53_id.id
        elif partner.wht_kind == 'pp54':
            if payment_type in ('outbound', 'purchase'):
                method = self.env.company.payment_method54_id.id
        return method

    @api.model
    def craete_wht_doc(self, payment, vals, account_currency, att):
        wizard = self
        account_wht_obj = self.env['account.wht']
        method = att['method']
        acc = method.account_id.id
        wht_id = account_wht_obj.create({
            'name': '/',
#             'payment_id': payment.id,
            'wht_type': payment.payment_type == 'inbound' and 'sale' or 'purchase',
            'account_id': acc,
            'date_doc': wizard.date_doc,
            'partner_id': att['partner'].id,
            'wht_kind': att['wht_kind'],
            'wht_payment': wizard.wht_payment,
            'line_ids': vals
        })
        return wht_id

    def create_wht(self):
        wizard = self
        active_id = self.env.context["active_id"]
        account_currency = self.env['res.currency'].search([('name', '=', 'THB')])
        group_partner = wizard.wht_ids.mapped('partner_id')
        for partner in group_partner:
            vals = []
            att = {'partner': partner, 'method': False, 'wht_kind': False}
            for line in self.wht_ids.sorted('partner_id'):
                if line.partner_id != partner:
                    continue
                att['method'] = line.payment_method_id
                att['wht_kind'] = line.wht_kind
                if not vals:
                    vals.append([0, 0, {
                        'date_doc': wizard.date_doc,
                        'wht_type_id': line.wht_type.id,
                        'base_amount': line.wht_base,
                        'rounding': line.rounding,
                        'percent': line.wht_rate,
                        'tax': line.total_wht,
                        'note': line.note,
                    }])
                else:
                    is_exist = False
                    for dic in vals:
                        if dic[2]['wht_type_id'] == line.wht_type.id and dic[2]['percent'] != line.wht_rate:
                            raise UserError('Sorry you can not choce same wht type and rate is not same')
                        elif dic[2]['wht_type_id'] == line.wht_type.id and dic[2]['percent'] == line.wht_rate:
                            dic[2]['base_amount'] += line.wht_base
                            dic[2]['tax'] += line.total_wht
                            is_exist = True
                    if not is_exist:
                        vals.append([0, 0, {
                            'date_doc': wizard.date_doc,
                            'wht_type_id': line.wht_type.id,
                            'base_amount': line.wht_base,
                            'rounding': line.rounding,
                            'percent': line.wht_rate,
                            'tax': line.total_wht,
                            'note': line.note,
                        }])

            if vals and att['method'] and att['wht_kind']:
                payment = self.env['account.payment'].browse(active_id)
                account_payment_line = self.env['account.payment.line']
                wht_id = self.craete_wht_doc(payment, vals, account_currency, att)
#                 if payment.payment_type == 'outbound':
#                     wht_tax = -wht_id.tax
#                 else:
                wht_tax = wht_id.tax
                account_payment_line.create({
                    'payment_id': payment.id,
                    'payment_method_id': att['method'].id,
                    'wht_id': wht_id.id,
                    'paid_total': wht_tax,
                })
                payment.amount += wht_id.tax


class PaymentMakeWhtLine(models.TransientModel):
    _name = "payment.make.wht.line"
    _description = "Payment Make WHT Line"

    @api.depends('wht_base','wht_type','wht_rate','rounding')
    def _compute_total_wht(self):
        for rec in self:
            rec.total_wht = round(rec.wht_base * (rec.wht_rate * 0.01), 2) + rec.rounding

    @api.onchange('wht_type')
    def onchange_type(self):
        for rec in self:
            rec.wht_rate = rec.wht_type.percentage

    @api.onchange('wht_kind')
    def onchange_wht_kind(self):
        """docstring for onchange_wht_kind"""
        for rec in self:
            name_search = ''
            if rec.wht_kind == 'pp4':
                name_search = 'หัก ณ ที่จ่าย (PND3)'
            elif rec.wht_kind == 'pp54':
                name_search = 'หัก ณ ที่จ่าย (PND54)'
            elif rec.wht_kind == 'pp7':
                active_id = rec._context.get('active_id')
                payment = self.env[rec._context.get('active_model')].browse([active_id])
                if payment.payment_type == 'inbound':
                    name_search = 'ถูกหัก ณ ที่จ่าย (PND53)'
                elif payment.payment_type == 'outbound':
                    name_search = 'หัก ณ ที่จ่าย (PND53)'
            if name_search:
                method = self.env['account.payment.method.multi'].search([('name', '=', name_search)])
                if method:
                    rec.payment_method_id = method[0].id

    wht_payment_id = fields.Many2one(
        'payment.make.wht'
    )
    invoice_id = fields.Many2one(
        'account.move',
        string='Invoice'
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Partner',
        related='invoice_id.partner_id',
    )
    wht_type = fields.Many2one(
        'account.wht.type',
        string = 'WHT',
        required=True,
    )
    wht_kind =  fields.Selection([
        ('pp4','(4) PND3'),
        ('pp7','(7) PND53'),
        ('pp54','PND54')],
        string = 'Type',
        required = True
    )
    payment_method_id = fields.Many2one(
        'account.payment.method.multi',
        ondelete="cascade",
        string='Payment Method WHT',
        required = True,
    )
    rounding = fields.Float(
        string='Adjust',
        default=0.0,
    )
    wht_rate = fields.Float(
        string="Rate",
        required=True,
    )
    wht_base = fields.Float(
        string='Base',
        digits='Product Price'
    )
    total_wht = fields.Float(
        string='Total WHT',
        compute='_compute_total_wht',
        digits='Product Price'
    )
    note = fields.Text(
        string = 'Note'
    )
