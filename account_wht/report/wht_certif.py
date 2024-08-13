# -*- encoding: utf-8 -*-
import odoo
from odoo import api, fields, models, _

from .report_tools import pdf_fill, pdf_merge
#from pdf_tools import pdf_fill,pdf_merge

from .num2word import num2word_th, fmt_tin, fmt_addr,fmt_new_addr
from .bahttext import bahttext

class WHTCertif(models.TransientModel):
    _name = 'wht.cerif.report'
    _description = 'WHT Certif Report'

    data = fields.Binary(
        string='Data',
    )

    def print_report(self, ids):
        env = self.env
        #print "WHT certificate report"

        lang = env['res.lang'].browse([1])
        user = env['res.users'].browse([1])
        # user=pool.get("res.users").browse(cr,uid,uid)
        pdf = False
        for id in ids:
            vouch = env['account.wht'].browse([id])
            # vouch = pool.get("account.wht").browse(cr,uid,id)
            # partner = vouch.company_id.partner_id
            partner = vouch.company_id.partner_id
            supp = vouch.partner_id

            year=vouch.date_doc.year+543
            month=vouch.date_doc.month
            day=vouch.date_doc.day
            if month == 1:
                month = u'มกราคม'
            elif month == 2:
                month = u'กุมภาพันธ์'
            elif month == 3:
                month = u'มีนาคม'
            elif month == 4:
                month = u'เมษายน'
            elif month == 5:
                month = u'พฤษภาคม'
            elif month == 6:
                month = u'มิถุนายน'
            elif month == 7:
                month = u'กรกฎาคม'
            elif month == 8:
                month = u'สิงหาคม'
            elif month == 9:
                month = u'กันยายน'
            elif month == 10:
                month = u'ตุลาคม'
            elif month == 11:
                month = u'พฤศจิกายน'
            elif month == 12:
                month = u'ธันวาคม'

            totals={}
            #totals[line.tax_code_id.code]=vouch.base_amount
            #print "totals",totals

            vals={
                "name1": partner.name if vouch.wht_type=='purchase' else supp.name,
                "add1": fmt_addr(partner) or "" if vouch.wht_type=='purchase' else supp and fmt_new_addr(supp) or "",
                "tin1": "",
                "id1": partner.vat and fmt_tin(partner.vat) or "" if vouch.wht_type=='purchase' else supp.vat and fmt_tin(supp.vat) or "",
                "name2": supp.name if vouch.wht_type =="purchase" else partner.name,
#                 "add2": supp and num2word.fmt_new_addr(supp) or "" if vouch.wht_type=='purchase' else num2word.fmt_addr(partner) or "",
                "add2": supp and fmt_addr(supp) or "",
                "id1_2": supp.vat and fmt_tin(supp.vat) or "" if vouch.wht_type=='purchase' else partner.vat and fmt_tin(partner.vat) or "",
                "tin1_2":  "",
                "run_no": vouch.name,
                "date_pay": day,
                "month_pay": month,
                "year_pay": year,
            }


            if vouch.wht_kind == 'pp1':
                vals.update({'chk1': "Yes"})
            if vouch.wht_kind == 'pp2':
                vals.update({'chk2': "Yes"})
            if vouch.wht_kind == 'pp3':
                vals.update({'chk3': "Yes"})
            if vouch.wht_kind == 'pp4':
                vals.update({'chk4': "Yes"})
            if vouch.wht_kind == 'pp5':
                vals.update({'chk5': "Yes"})
            if vouch.wht_kind == 'pp6':
                vals.update({'chk6': "Yes"})
            if vouch.wht_kind == 'pp7':
                vals.update({'chk7': "Yes"})

            if vouch.wht_payment == 'pm1':
                vals.update({'chk8': "Yes"})
            if vouch.wht_payment == 'pm2':
                vals.update({'chk9': "Yes"})
            if vouch.wht_payment == 'pm3':
                vals.update({'chk10': "Yes"})
            if vouch.wht_payment == 'pm4':
                vals.update({'chk11': "Yes"})

            #Item No
            vals.update({'item':vouch.seq or ""})


            total_base=vouch.base_amount
            total_tax=vouch.tax

            for line in vouch.line_ids:
                year=line.date_doc.year+543
                month=line.date_doc.month
                day=line.date_doc.day
                if line.wht_type_id.seq == 100:
                    vals.update({
                        "date1": "%d-%d-%d"%(day,month,year),
                        "pay1.0": lang.format("%.2f",line.base_amount,grouping=True).replace("."," "),
                        "tax1.0": lang.format("%.2f",line.tax,grouping=True).replace("."," "),
                    })
                if line.wht_type_id.seq == 200:
                    vals.update({
                        "date2": "%d-%d-%d"%(day,month,year),
                        "pay1.1": lang.format("%.2f",line.base_amount,grouping=True).replace("."," "),
                        "tax1.1": lang.format("%.2f",line.tax,grouping=True).replace("."," "),
                    })
                if line.wht_type_id.seq == 300:
                    vals.update({
                        "date3": "%d-%d-%d"%(day,month,year),
                        "pay1.2": lang.format("%.2f",line.base_amount,grouping=True).replace("."," "),
                        "tax1.2": lang.format("%.2f",line.tax,grouping=True).replace("."," "),
                    })
                if line.wht_type_id.seq == 400:
                    vals.update({
                        "date4": "%d-%d-%d"%(day,month,year),
                        "pay1.3": lang.format("%.2f",line.base_amount,grouping=True).replace("."," "),
                        "tax1.3": lang.format("%.2f",line.tax,grouping=True).replace("."," "),
                    })
                if line.wht_type_id.seq == 411:
                    vals.update({
                        "date5": "%d-%d-%d"%(day,month,year),
                        "pay1.4": lang.format("%.2f",line.base_amount,grouping=True).replace("."," "),
                        "tax1.4": lang.format("%.2f",line.tax,grouping=True).replace("."," "),
                    })
                if line.wht_type_id.seq == 412:
                    vals.update({
                        "date6": "%d-%d-%d"%(day,month,year),
                        "pay1.5": lang.format("%.2f",line.base_amount,grouping=True).replace("."," "),
                        "tax1.5": lang.format("%.2f",line.tax,grouping=True).replace("."," "),
                    })
                if line.wht_type_id.seq == 413:
                    vals.update({
                        "date7": "%d-%d-%d"%(day,month,year),
                        "pay1.6": lang.format("%.2f",line.base_amount,grouping=True).replace("."," "),
                        "tax1.6": lang.format("%.2f",line.tax,grouping=True).replace("."," "),
                    })
                if line.wht_type_id.seq == 414:
                    vals.update({
                        #rate1
                        "rate1": "",
                        "date8": "%d-%d-%d"%(day,month,year),
                        "pay1.7": lang.format("%.2f",line.base_amount,grouping=True).replace("."," "),
                        "tax1.7": lang.format("%.2f",line.tax,grouping=True).replace("."," "),
                    })
                if line.wht_type_id.seq == 421:
                    vals.update({
                        "date9": "%d-%d-%d"%(day,month,year),
                        "pay1.8": lang.format("%.2f",line.base_amount,grouping=True).replace("."," "),
                        "tax1.8": lang.format("%.2f",line.tax,grouping=True).replace("."," "),
                    })
                if line.wht_type_id.seq == 422:
                    vals.update({
                        "date10": "%d-%d-%d"%(day,month,year),
                        "pay1.9": lang.format("%.2f",line.base_amount,grouping=True).replace("."," "),
                        "tax1.9": lang.format("%.2f",line.tax,grouping=True).replace("."," "),
                    })
                if line.wht_type_id.seq == 423:
                    vals.update({
                        "date11": "%d-%d-%d"%(day,month,year),
                        "pay1.10": lang.format("%.2f",line.base_amount,grouping=True).replace("."," "),
                        "tax1.10": lang.format("%.2f",line.tax,grouping=True).replace("."," "),
                    })
                if line.wht_type_id.seq == 425:
                    vals.update({
                        "spec1": line.name,
                        "date12": "%d-%d-%d"%(day,month,year),
                        "pay1.11": lang.format("%.2f",line.base_amount,grouping=True).replace("."," "),
                        "tax1.11": lang.format("%.2f",line.tax,grouping=True).replace("."," "),
                    })
                if line.wht_type_id.seq == 500:
                    vals.update({
                        "date13": "%d-%d-%d"%(day,month,year),
                        "pay1.12": lang.format("%.2f",line.base_amount,grouping=True).replace("."," "),
                        "tax1.12": lang.format("%.2f",line.tax,grouping=True).replace("."," "),
                    })
                if line.wht_type_id.seq == 600:
                    vals.update({
                        "spec3": line.note or vouch.note or line.wht_type_id.printed or 'ค่าบริการ',
                        "date14": "%d-%d-%d"%(day,month,year),
                        "pay1.13": lang.format("%.2f",line.base_amount,grouping=True).replace("."," "),
                        "tax1.13": lang.format("%.2f",line.tax,grouping=True).replace("."," "),
                    })

            vals.update({
                "pay1.14": lang.format("%.2f",total_base,grouping=True).replace("."," "),
                "tax1.14": lang.format("%.2f",total_tax,grouping=True).replace("."," "),
                "total": bahttext(total_tax),
            })

            pdf2=pdf_fill("wht_certif.pdf",vals)
            if pdf:
                pdf = pdf_merge(pdf, pdf2)
            else:
                pdf = pdf2
        return pdf
#         self.write({
#             'data': pdf
#         })
#         filename = 'wht_certif.pdf'
#         return {
#             'type': 'ir.actions.act_url',
#             'url': '/web/content/wht.cerif.report/%s/data/%s?download=true' %(self.id,filename),
#         }
#         return (pdf, "pdf")

# report_custom("report.wht.certif")
