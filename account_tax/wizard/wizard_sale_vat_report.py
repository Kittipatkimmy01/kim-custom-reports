# -*- coding: utf-8 -*-

import base64
import locale
import re
import calendar

from odoo import fields, models, api, _
from io import StringIO,BytesIO
from datetime import datetime,timedelta
from dateutil.relativedelta import relativedelta

try:
    import xlwt
except ImportError:
    xlwt = None

CLEANR = re.compile('<.*?>')
TAG_RE = re.compile(r'<[^>]+>')

class WizardSaleVatReport(models.TransientModel):
    _name = 'wizard.sale.vat.report'
    _description = 'Wizard Sale Vat Report'

    account_id = fields.Many2one(
        string='Account Code',
        comodel_name='account.account',
        readonly=False,
    )
    month = fields.Selection(
        [
            ('1', 'มกราคม'),
            ('2', 'กุมภาพันธ์'),
            ('3', 'มีนาคม'),
            ('4', 'เมษายน'),
            ('5', 'พฤษภาคม'),
            ('6', 'มิถุนายน'),
            ('7', 'กรกฎาคม'),
            ('8', 'สิงหาคม'),
            ('9', 'กันยายน'),
            ('10', 'ตุลาคม'),
            ('11', 'พฤศจิกายน'),
            ('12', 'ธันวาคม'),
        ],
        string='Month',
        type='selection',
    )
    year = fields.Char(
        string = "Year",
        default = fields.date.today().strftime("%Y"),
    )
    data = fields.Binary(
        string='Data'
    )
    filename = fields.Char(
        string='File Name',
    )

    api.model
    def default_get(self, fields):
        res = super(WizardSaleVatReport, self).default_get(fields)
        company = self.env.company
        account_sale_tax_id = company.account_sale_vat_report_id
#         vat_sale = False
#         for l in account_sale_tax_id.invoice_repartition_line_ids:
#             if l.account_id:
#                 vat_sale = l.account_id
#         if vat_sale:
        if account_sale_tax_id:
            res['account_id'] = account_sale_tax_id.id
        return res

    def print_report(self):
        """docstring for print_report"""
        if xlwt:
            workbook = xlwt.Workbook()
            worksheet = workbook.add_sheet('Sale Vat Report')
            workbook.set_colour_RGB(0x22, 215, 165, 218)
            xlwt.add_palette_colour('custom_color02', 0x22)

            workbook.set_colour_RGB(0x21, 114, 178, 218)
            xlwt.add_palette_colour('custom_color01', 0x21)

            workbook.set_colour_RGB(0x23, 224, 224, 224)
            xlwt.add_palette_colour('custom_color03', 0x23)

            h0_style = xlwt.easyxf('font: bold 1,name TH SarabunPSK, height 200;'
                                   'align: vert center, horz center ,wrap yes;')

            h0_style02 = xlwt.easyxf('font: bold 1,name TH SarabunPSK, height 200;'
                                    'pattern: pattern solid, fore_colour custom_color01;'
                                    'align: horiz left;')

            base_style = xlwt.easyxf('font: name TH SarabunPSK, height 200;'
                                     'align: vert center, horz center ,wrap yes')

            left_base_style = xlwt.easyxf('font: name TH SarabunPSK, height 200;'
                                          'align: vert center, horz left,wrap yes')

            base_style02 = xlwt.easyxf('font: bold 1, name TH SarabunPSK, height 200;'
                                    'pattern: pattern solid, fore_colour custom_color02;'
                                     'align: vert center, horz center ,wrap yes')

            base_style03 = xlwt.easyxf('font: name TH SarabunPSK, height 200;'
                                    'pattern: pattern solid, fore_colour custom_color03;'
                                     'align: vert center, horz center ,wrap yes')

            h1_style = xlwt.easyxf('font: name TH SarabunPSK, height 200;'
                                     'align: vert top, horz left, wrap yes;')

            h2_style = xlwt.easyxf('font: name TH SarabunPSK, height 200;'
                                     'align: vert top, horz right, wrap yes;')

            h3_style = xlwt.easyxf('font: name TH SarabunPSK, height 200;'
                                   'align: vert center, horz left, wrap yes;')

            h0_number_style = xlwt.easyxf(
                'font:bold 1, name TH SarabunPSK, height 200;'
                'borders: top_color black, bottom_color black, right_color black, left_color black,\
                              left thin, right thin, top thin, bottom double;'
                'pattern: pattern solid, fore_color white;'
                'align: vert center, horz right ,wrap yes', num_format_str='#,##0.00')

            base_number_style = xlwt.easyxf(
                'font: name TH SarabunPSK, height 200;'
                'align: vert center, horz right ,wrap yes', num_format_str='#,##0.00')

            base_number_style02 = xlwt.easyxf(
                'font: name TH SarabunPSK, height 200;'
                'pattern: pattern solid, fore_colour custom_color02;'
                'align: vert center, horz right ,wrap yes', num_format_str='#,##0.00')

            base_number_style03 = xlwt.easyxf(
                'font: name TH SarabunPSK, height 200;'
                'pattern: pattern solid, fore_colour custom_color03;'
                'align: vert center, horz right ,wrap yes', num_format_str='#,##0.00')

            minus_number_style = xlwt.easyxf(
                'font: name TH SarabunPSK, height 200;'
                'align: vert center, horz right ,wrap yes', num_format_str='(#,##0.00)')


            row = 5
            col = 0
            TaxLine = self.env['account.tax.line']
            wizard = self
            month = wizard.month
            # month_val = dict(self._columns['month'].selection).get(month)
            month_val = dict(self._fields['month'].selection).get(self.month)
            year = wizard.year

            lang = self.create_uid.lang
            if lang == 'th_TH':
                years = int(year) + 543
            else:
                years = int(year)

            conv_date = year + '-' + month + '-' + '1'
            date_start = datetime.strptime(conv_date, "%Y-%m-%d").date()
            date_end = ((date_start + relativedelta(months=1)) - relativedelta(days=1))
            date_start = datetime.strftime(date_start, "%Y-%m-%d")
            date_end = datetime.strftime(date_end, "%Y-%m-%d")
            domain = [('account_id', '=', self.account_id.id)]
            string_filter = ""
            if date_start and date_end:
                domain += [('month_vat', '=', month), ('year', '=', year),('is_verify','=',True)]
                string_filter += u" วันที่ " + date_start + u" ถึง " + date_end + " "
            order = "date,id asc"
            tax0 = self.env['account.tax'].search([('amount', '=', 0),('type_tax_use', '=', 'sale')])
            d_start = str(year) + '-' + str(month) + '-01'
            days_month = calendar.monthrange(int(year), int(month))
            d_end = str(year) + '-' + str(month) + '-' + str(days_month[1])
            start_date = ''
            domain_vat0 = [('tax_ids', 'in', tax0.ids),('move_id.invoice_date', '>=', d_start),('move_id.invoice_date', '<=', d_end)]

            row = 5
            col = 0
            sum_month = sum_residual = sum_payment = 0
            no = 1
#             company = self.env['res.company'].browse(1)
            company = self.env.user.company_id
            company_name = company.name
            sale_move = False
            # sale_acc_name = int(self.account)
            # purchase_acc_name = int(self.account)
            sale_move = False
            header_name = u"รายงานภาษีขาย (Sales Tax Report)"
            worksheet.write_merge(row - 5, row - 5, col, col + 10, header_name, h0_style)
            worksheet.write_merge(row - 4, row - 4, col, col + 1, u"ชื่อผู้ประกอบการ", base_number_style)
            worksheet.write_merge(row - 4, row - 4, col + 2, col + 6, company_name, h3_style)
            worksheet.write_merge(row - 4, row - 4, col + 7, col + 8, u"เลขประจำตัวผู้เสียภาษี", h0_style)
            worksheet.write_merge(row - 4, row - 4, col + 9, col + 10, company.vat, h0_style)
            worksheet.write_merge(row - 3, row - 2, col, col + 1, u"สถานประกอบการ", h2_style)
            worksheet.write_merge(row - 3, row - 2, col + 2, col + 6, company.street, h1_style)
            worksheet.write_merge(row - 3, row - 3, col + 7, col + 7, u"เดือน/ปี", h0_style)
            worksheet.write_merge(row - 2, row - 2, col + 7, col + 7, u"{0}/{1}".format(month_val,years), h0_style)
            worksheet.write_merge(row - 3, row - 3, col + 8, col + 8, u"สาขา", h0_style)
            worksheet.write_merge(row - 3, row - 3, col + 9, col + 10, u"00000", h0_style)
            worksheet.write_merge(row - 2, row - 2, col + 8, col + 8, u"หน้า", h0_style)
            worksheet.write_merge(row - 1, row - 1, col + 7, col + 8, u"สถานประกอบการ", h0_style)
            worksheet.write(row, col, u"ลำดับ", h0_style)
            worksheet.write(row, col + 1, u"วันที่/เดือน/ปี", h0_style)
            worksheet.write(row, col + 2, u"ใบกำกับภาษี", h0_style)
            worksheet.write(row, col + 3, u"เลขที่อ้างอิง", h0_style)
            worksheet.write(row, col + 4, u"เลขที่ออกใหม่", h0_style)
            worksheet.write(row, col + 5, u"ชื่อผู้ซื้อสินค้า/บริการ", h0_style)
            worksheet.write(row, col + 6, u"เลขประจำตัวผู้เสียภาษี", h0_style)
            worksheet.write(row, col + 7, u"สำนักงานใหญ่", h0_style)
            worksheet.write(row, col + 8, u"สาขา", h0_style)
            worksheet.write(row, col + 9, u"มูลค่าสินค้า/บริการ", h0_style)
            worksheet.write(row, col + 10, u"ภาษีมูลค่าเพิ่ม", h0_style)
            worksheet.write(row, col + 11, u"ยอดรวม", h0_style)
            worksheet.write(row, col + 12, u"หมายเหตุ", h0_style)

            worksheet.row(row - 5).height = 400
            worksheet.row(row - 4).height = 400
            worksheet.row(row - 3).height = 400
            worksheet.row(row - 2).height = 400
            worksheet.row(row - 1).height = 400
            worksheet.col(col).width = 1200
            worksheet.col(col + 1).width = 3500
            worksheet.col(col + 2).width = 3500
            worksheet.col(col + 3).width = 3500
            worksheet.col(col + 4).width = 3500
            worksheet.col(col + 5).width = 10000
            worksheet.col(col + 6).width = 5000
            worksheet.col(col + 7).width = 3000
            worksheet.col(col + 8).width = 3000
            worksheet.col(col + 9).width = 5000
            worksheet.col(col + 10).width = 3500
            worksheet.col(col + 11).width = 3500
            worksheet.col(col + 12).width = 5000

            row += 1
            tax_list = []
            total_base = total_tax = total_amount = 0.0
            tax_lns = TaxLine.search(domain,order=order)
            for taxl in tax_lns:
                obj = self.env[taxl.res_model].browse(taxl.res_id)
                partner_name = partner_number = partner_branch = move_name =False
                base = taxl.base
                tax_amount = taxl.amount
                move_name = obj.name
                partner_name = taxl.partner_id.name
                partner_number = taxl.partner_id.vat or '-'
                partner_branch = taxl.partner_id.branch
                tax_date = datetime.strftime(taxl.date, "%d/%m/%Y")
                tax_list.append({
                    'date': tax_date,
                    'vat_ref': taxl.vat_ref or "-",
                    'origin_ref': "-",
                    'partner_name': partner_name,
                    'partner_number': partner_number,
                    'branch_main': 'X' if partner_branch == '00000' else " ",
                    'branch': partner_branch if partner_branch != '00000' else ' ',
                    'base': round(base, 2),
                    'tax_amount': abs(round(tax_amount, 2)),
                    'total': round(base + abs(tax_amount), 2),
                })
            #### Write Data ####
            for txl in tax_list:
                worksheet.write(row, col, no, base_style)
                worksheet.write(row, col + 1, txl['date'], base_style)
                worksheet.write(row, col + 2, txl['vat_ref'], base_style)
                worksheet.write(row, col + 3, txl['origin_ref'], base_style)
                worksheet.write(row, col + 4, u"{0}/{1}".format(str(month).zfill(2),str(no).zfill(3)), base_style)
                worksheet.write(row, col + 5, txl['partner_name'], base_style)
                worksheet.write(row, col + 6, txl['partner_number'], base_style)
                worksheet.write(row, col + 7, txl['branch_main'], base_style)
                worksheet.write(row, col + 8, txl['branch'], base_style)
                worksheet.write(row, col + 9, txl['base'], base_number_style)
                worksheet.write(row, col + 10, txl['tax_amount'], base_number_style)
                worksheet.write(row, col + 11, txl['total'], base_number_style)
#                 if abs(tax_amount) == 0:
#                     worksheet.write(row, col + 12, tax.invoice_id.name or '', base_style)

                worksheet.row(row).height = 400
                total_base += txl['base']
                total_tax += txl['tax_amount']
                total_amount += txl['total']
                no += 1
                row += 1

            worksheet.write(row, col + 6, u"ยอดรวมภาษีประจำเดือน", h0_style)
            worksheet.write(row, col + 9, total_base, h0_number_style)
            worksheet.write(row, col + 10, total_tax, h0_number_style)
            worksheet.write(row, col + 11, total_amount, h0_number_style)


            fp = BytesIO()
            workbook.save(fp)
            fp.seek(0)
            report_name = "Sale_Vat_Report"
            month_name = calendar.month_name[int(self.month)]
            filename = '%s_%s-%s.xls' % (report_name, month_name, self.year)
            self.write({
                'data': base64.encodebytes(fp.read()),
                'filename': filename,
            })
            fp.close()
            return {
                'type': 'ir.actions.act_url',
                'url': '/web/content/wizard.sale.vat.report/%s/data/%s?download=true' %(self.id,filename),
            }
