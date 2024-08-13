# -*- coding: utf-8 -*-

from odoo import fields, models, api
import decimal
import base64


class account_wht_type(models.Model):
    _name = "account.wht.type"
    _description = "Type of WHT"
    _order = 'seq'

    code = fields.Char('Code', size=256, required=False)
    name = fields.Char('Description', size=256, required=True)
    printed = fields.Char('Printed', size=32)
    seq = fields.Integer('Sequence')
    percentage = fields.Float('Percentage')

    _sql_constraints = [
        ('seq_unique', 'unique (seq)', 'Sequence must be unique !')
    ]

class account_wht(models.Model):

    _name = 'account.wht'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "With holding tax"
    _order = "date_doc desc, name desc"

    def _compute_tax(self):
        result = {}
        for id in self:
            result[id] = {
                'tax': 0.0,
                'base_amount': 0.0,
            }
            data = self.browse([id])[0]
            val = val1 = 0.0
            for line in data.id.line_ids:
                val1 += line.base_amount
                val += line.tax
            id.tax = val
            id.base_amount = val1

    def _get_line(self):
        result = {}
        for line in self.env['account.wht.line'].browse(self.ids):
            if line:
                result[line.wht_id.id] = True
        return result.keys()

    name = fields.Char('No.', size=32, required=True, default='/')
    date_doc = fields.Date('Document Date', default=fields.Datetime.now)
    company_id = fields.Many2one(
        'res.company',
        'Company',
        required=True,
        default=lambda self: self.env['res.company']._company_default_get('account.wht')
    )
    partner_id=  fields.Many2one('res.partner','Partner', required=True)
    account_id = fields.Many2one('account.account','Account', required=False)
    seq = fields.Integer('Sequence')
    wht_type = fields.Selection([
            ('sale','With holding tax (Sale)'),
            ('purchase','With holding tax (Purchase)')
        ],
        'Type of WHT',
        default="purchase"
    )
    wht_kind = fields.Selection([
            ('pp1','(1) PND1'),
            ('pp2','(2) PND1'),
            ('pp3','(3) PND2'),
            ('pp4','(4) PND3'),
            ('pp5','(5) PND2'),
            ('pp6','(6) PND2'),
            ('pp7','(7) PND53'),
            ('pp54','PND54'),
        ],
        'Kind of WHT',
        default='pp4'
    )
    wht_payment = fields.Selection([
            ('pm1','(1) With holding tax'),
            ('pm2','(2) Forever'),
            ('pm3','(3) Once'),
            ('pm4','(4) Other'),
        ],
        'WHT Payment',
        default='pm1'
    )
    note = fields.Text('Note')
    line_ids = fields.One2many('account.wht.line', 'wht_id', 'WHT Line')
    base_amount = fields.Float(
        compute='_compute_tax',
        digits="Product Price",
        string='Base Amount'
    )
    tax = fields.Float(
        compute='_compute_tax',
        digits="Product Price",
        string='Tax',
        tracking=1,
    )
    state = fields.Selection([
            ('draft', 'Draft'),
            ('cancel', 'Cancelled'),
            ('done', 'Done'),
        ],
        'Status',
        readonly=True,
        default='draft'
    )
    payment_count = fields.Integer(
        string='Payment Count',
        compute='_compute_payment_count',
    )
    download_by = fields.Many2one('res.users','Download By',
        tracking=1,
    )
    pnd_ids = fields.Many2many(
        'account.wht.pnd',
        'account_wht_pnds',
        'wht_id',
        'pnd_id',
        'With holding tax'
    )
    data = fields.Binary(
        string='Data',
    )
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Currency',
    )

    def _compute_payment_count(self):
        for rec in self:
            payment_line = self.env['account.payment.line']
            line_payment = payment_line.search([('wht_id', '=', rec.id)])
            if line_payment:
                payment = line_payment.mapped('payment_id')
                rec.payment_count = len(payment)
            else:
                rec.payment_count = 0

    def print_report_wht_certificate(self):
        res = self.env['wht.cerif.report'].print_report(self.ids)
        self.write({
            'data': base64.encodebytes(res)
        })
        filename = 'wht_certif.pdf'
        self.download_by = self.env.user.id
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/account.wht/%s/data/%s?download=true' %(self.id,filename),
        }
#         return res
    def action_view_payment(self):
        payment_line = self.env['account.payment.line']
        line_payment = payment_line.search([('wht_id', '=', self.id)])
        objs = line_payment.mapped('payment_id')
        if objs:
            if objs[0].payment_type == 'inbound':
                action = self.env.ref('account.action_account_payments').read()[0]
            elif objs[0].payment_type == 'outbound':
                action = self.env.ref('account.action_account_payments_payable').read()[0]
        view_id = self.env.ref('account.view_account_payment_form').id
        if len(objs) > 1:
            action['domain'] = [('id', 'in', objs.ids)]
        elif len(objs) == 1:
            action['views'] = [(view_id, 'form')]
            action['res_id'] = objs.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    @api.onchange("wht_kind")
    def onchange_wht_kind(self):
        default = {
            'value':{},
        }

        if self._context == 'pp4':
            default['value']['account_id'] = self.env['res.users'].browse([]).company_id.account_wht_pp3.id
        elif self._context == 'pp7':
            default['value']['account_id'] = self.env['res.users'].browse([]).company_id.account_wht_pp53.id
        elif self._context == 'pp54':
            default['value']['account_id'] = self.env['res.users'].browse([]).company_id.account_wht_pp54.id
        return default

    @api.onchange('partner_id')
    def on_change_partner(self):
        value = {}
        if self.partner_id:
            value = {'wht_kind': self.partner_id.wht_kind or False}
        return {'value': value}

    def copy(self, default=None):
        if not default:
            default = {}
        wht_type = default.get('wht_type','/')
        date_doc = default.get('date_doc')
        if wht_type == 'sale':
            name = self.env['ir.sequence'].with_context(ir_sequence_date=date_doc).next_by_code('account.wht') or '/'
        else:
            name = self.env['ir.sequence'].with_context(ir_sequence_date=date_doc).next_by_code('account.wht.vendor') or '/'
        default.update({
            'line_ids':False,
#             'voucher_id':False,
            'name': name,
        })
        return super(account_wht, self).copy(default)

    @api.model_create_multi
    def create(self, vals):
        for val in vals:
            if val.get('name','/')=='/':
                val['name'] = 'draft'
#                 wht_type = val.get('wht_type','/')
#                 date_doc = val.get('date_doc')
#                 if wht_type == 'sale':
#                     val['name'] = self.env['ir.sequence'].with_context(ir_sequence_date=date_doc).next_by_code('account.wht') or '/'
#                 else:
#                     val['name'] = self.env['ir.sequence'].with_context(ir_sequence_date=date_doc).next_by_code('account.wht.vendor') or '/'
        return super(account_wht, self).create(vals)

    def button_compute_tax(self):

        for wht in self:
            tax_amount = tax = 0.0
            for line in wht.line_ids:
                tax = (((line.percent / 100) or 0.0) * line.base_amount) or 0.0
                line.write({'tax': tax})
                tax_amount += tax
            wht.write({'tax': tax_amount})
        return True

    def action_cancel(self):
        self.write({'state': 'cancel'})
        return True

    def action_done(self):
        obj = self.browse(self.ids)
        if 'draft' in obj.name:
            if obj.wht_type == 'sale':
                name = self.env['ir.sequence'].with_context(ir_sequence_date=self.date_doc).next_by_code('account.wht') or '/'
            else:
                name = self.env['ir.sequence'].with_context(ir_sequence_date=self.date_doc).next_by_code('account.wht.vendor') or '/'
            self.write({'name': name})
        self.write({'state': 'done'})
        return True

    def action_draft(self):
        self.write({'state': 'draft'})
        return True

    def print_wht(self):
        return self.env['report'].get_action('wht.certif')

    def month_name(self, month):
        """docstring for month_name"""
        month = ''
        if month == '01':
            month = 'มกราคม'
        if month == '02':
            month = 'กุมภาพันธ์'
        if month == '03':
            month = 'มีนาคม'
        if month == '04':
            month = 'เมษายน'
        if month == '05':
            month = 'พฤษภาคม'
        if month == '06':
            month = 'มิถุนายน'
        if month == '07':
            month = 'กรกฎาคม'
        if month == '08':
            month = 'สิงหาคม'
        if month == '09':
            month = 'กันยายน'
        if month == '10':
            month = 'ตุลาคม'
        if month == '11':
            month = 'พฤศิกายน'
        if month == '12':
            month = 'ธันวาคม'
        return month


class account_wht_line(models.Model):

    _name = 'account.wht.line'
    _description = "WHT Line"

    @api.model
    def _compute_tax(self):
        company_id = self.env['res.company']._company_default_get('account.wht')
        for data in self:
#             total = round((((data.percent / 100) or 0.0) * data.base_amount),2) or 0.0
#             tax = decimal.Decimal(str(total)).quantize(decimal.Decimal('.01'), rounding=decimal.ROUND_UP)
            tax = round(data.base_amount * (data.percent * 0.01), 2)
            data.tax_invoice = (float(tax) + data.rounding)

    name = fields.Char('Description', size=128, default='/')
    wht_type_id = fields.Many2one('account.wht.type','Type',required=True)
    date_doc = fields.Date('Date', required=True, default=fields.Datetime.now)
    percent = fields.Float('Percent', digits="Product Price", required=True, default=3.0)
    base_amount = fields.Float('Base Amount', digits="Product Price", required=True)
    rounding = fields.Float(
        string='Adjust',
        default=0.0,
    )
    tax = fields.Float(
        digits="Product Price",
        string='Tax'
    )
    tax_invoice = fields.Float(
        compute="_compute_tax",
        string='Withoding Amount',
    )
    wht_id = fields.Many2one('account.wht','WHT')
    note = fields.Char('Note', size=64)
    type = fields.Selection([('1','หัก ณ ที่จ่าย (1)'),('2','ออกภาษีให้ (2)')], 'Condition', required=True, index=True, default='1')

    @api.onchange('percent', 'base_amount', 'rounding')
    def onchange_tax(self):
        """docstring for onchange_"""
        for rec in self:
            tax = (round(rec.base_amount * (rec.percent * 0.01), 2) + rec.rounding)
            rec.tax = tax

    def copy(self, default=None):
        if not default:
            default = {}
        default.update({
            'wht_id':False,
        })
        return super(account_wht_line, self).copy(default)


class account_wht_pnd(models.Model):
    _name = 'account.wht.pnd'
    _description = "WHT PND"
    _inherit = 'mail.thread'

    def _compute_tax(self):
        result = {}
        for id in self.ids:
            result[id] = {
                'total_amount': 0.0,
                'total_tax': 0.0,
                'total_tax_send':0.0,
            }
            data = self.browse([id])[0]
            val = val1 = 0.0
            for line in data.wht_ids:
                val1 += line.base_amount
                val += line.tax

            data.total_tax = val
            data.total_amount = val1
            data.total_tax_send = val + data.add_amount or 0.0

    def _compute_line(self):
        result = {}
        for id in self.ids:
            result[id] = {
                'attach_count': 0,
                'attach_no': 0,
            }
            data = self.browse([id])[0]

            count_line = len(data.wht_ids)
            count_page = (count_line / 6) == 0 and 1 or (count_line / 6)
            self.attach_count = count_line
            self.attach_no = count_page

        return result

    name = fields.Char('Description', size=128, default='/')
    date_pnd = fields.Date('Date', required=True, default=fields.Datetime.now)
    type_normal =  fields.Boolean('Normal Type', default=True)
    type_special = fields.Boolean('Special Type')
    type_no = fields.Integer('Type No.')
    section_3 = fields.Boolean('Section 3')
    section_48 = fields.Boolean('Section 48')
    section_50 = fields.Boolean('Section 50')
    section_65 = fields.Boolean('Section 65')
    section_69 = fields.Boolean('Section 69')
    attach_pnd = fields.Boolean('Attach PND', default=True)
    attach_count = fields.Integer(compute="_compute_line",string='Attach Count')
    attach_no = fields.Integer(compute="_compute_line",string='Attach No')
    total_amount = fields.Float(compute="_compute_tax", digits="Product Price", string='Total Amount')
    total_tax = fields.Float(compute="_compute_tax", digits="Product Price", string='Total Tax')
    add_amount = fields.Float('Add Amount', digits="Product Price")
    total_tax_send = fields.Float(compute="_compute_tax", digits="Product Price", string='Total Tax Send')
    wht_ids = fields.Many2many('account.wht', 'account_wht_pnds', 'pnd_id', 'wht_id', 'With holding tax')
    note = fields.Text('Note')
    company_id = fields.Many2one(
        'res.company',
        'Company',
        required=True,
        default=lambda self: self.env['res.company']._company_default_get('account.wht.pnd')
    )
    pnd_type = fields.Selection([
            ('pp4','(4) PND3'),
            ('pp7','(7) PND53'),
            ('pp54','PND54')
        ],
        'PND Type',
        required=True,
        index=True
    )
    type_of_income = fields.Selection(
        selection=[
            ('1', '(1) Fee Commission or other under Section 40(2)'),
            ('2', '(2) Royalty for copyright, literacy, artistic, scientific work'),
            ('3', '(3) Patent fee, formula or secert process under section 40(3)'),
            ('4', '(4) Other royalty under Section 40(3)'),
            ('5', '(5) Interest under section 40(4)(a) paid to bank, insurance company or other similar business'),
            ('6', '(6) Other interest under section 40(4)(a)'),
            ('7', '(7) Devidends under section 40(4)(b)'),
            ('8', '(8) Other income under section 40(4)(Specify)'),
            ('9', '(9) Rent for ship at sea under Maritime Promotion Law'),
            ('10', '(10) Rent for money or other benefits under section 40(5)'),
            ('11', '(11) Income from liberal profession under section 40(6)(Specify)'),
        ],
        string='Type of Assessable Income',
    )
    download_by = fields.Many2one('res.users','Download By',
        tracking=1,
    )

    def print_report_wht_pnd(self):
        self.download_by = self.env.user.id
        if self.pnd_type == 'pp4':
            res = self.env['report'].get_action(self, 'wht.pnd3')
        elif self.pnd_type == 'pp7':
            res = self.env['report'].get_action(self, 'wht.pnd53')
        elif self.pnd_type == 'pp54':
            res = self.env['report'].get_action(self, 'wht.pnd54')
        return res

    def print_report_wht_pnd_attach(self):
        self.download_by = self.env.user.id
        if self.pnd_type=='pp4':
            res = self.env['report'].get_action(self, 'wht.pnd3.attach')
        elif self.pnd_type== 'pp7':
            res = self.env['report'].get_action(self, 'wht.pnd53.attach')

        return res

class account_account(models.Model):

    _inherit = "account.account"
    _order = 'code asc'

    account_wht = fields.Boolean('With Holding Tax')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
