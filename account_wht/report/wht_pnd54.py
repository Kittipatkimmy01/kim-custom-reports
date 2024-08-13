# -*- encoding: utf-8 -*-
import odoo
from odoo import api, fields, models, _
from openerp.report.interface import report_int
from report_tools import pdf_fill, pdf_merge
# from openerp.osv import fields, osv
#
# import openerp.pooler
from num2word import num2word_th, fmt_tin_pnd54, set_satang, fmt_thaidate
import datetime

class report_custom(report_int):
    def create(self,cr,uid,ids,datas,context={}):
        env = odoo.api.Environment(cr, uid, context or {})
        #print "WHT PND3 Report"      
        lang = env['res.lang'].browse([1])
        user = env['res.users'].browse([1])
        pdf = False
        for id in ids:
            vouch = env['account.wht.pnd'].browse([id])
            for pnd in vouch.wht_ids:
            # company = vouch.company_id.partner_id
            # company = vouch.company_id.partner_id
                wht_partner_id = env['ir.values'].get_default('account.config.wht', 'partner_wht_id',
                    company_id=env.user.company_id.id)
                company = env['res.partner'].browse(wht_partner_id)

                year=int(vouch.date_pnd[0:4])+543
                month=int(vouch.date_pnd[5:7]) - 1
                # if month == -1:
                #     month = 11
                if month == -1:
                    month = 11
                if month == 11:
                    month_radio = 11
                    year = year - 1
                elif month == 0:
                    month_radio = 1
                elif month == 1:
                    month_radio = 2
                elif month == 2:
                    month_radio = 3
                else:
                    month_radio = month
                #print month
                year_sign=int(vouch.date_pnd[0:4])+543
                #month=int(vouch.date_pnd[5:7]) - 1
                #month=int(vouch.date_pnd[5:7]) - 2
                month_sign = int(vouch.date_pnd[5:7])

                day=int(vouch.date_pnd[8:10])

                daynow = datetime.datetime.now().day
                monthnow  = datetime.datetime.now().month
                yearnow = int(datetime.datetime.now().year)+543

                typepnd = 0
                section3 = ""
                section65 = ""
                section69 = ""
                attachpnd = ""

                if vouch.type_normal == True:
                    typepnd = 0
                else:
                    typepnd = 1
                if  vouch.section_3 == True:
                    section3 = "Yes"
                if  vouch.section_65 == True:
                    section65 = "Yes"
                if  vouch.section_69 == True:
                    section69 = "Yes"
                if  vouch.attach_pnd == True:
                    attachpnd = "Yes"

                vals={
                    "Num1":company.number and fmt_tin_pnd54(company.number.strip()) or "",
                    # "Text3": company.tax_detail or '',
                    "Num2":company.branch or '00000',
                    "Text1":company.name,
                    "Text2":company.building or '',
                    "Text3":company.room_no or '',
                    "Text4":company.floor or '',
                    "Text8":'-',
                    "Text9":company.house_no or '',
                    "Text10":company.moo or '',
                    "Text11":company.alley or '',
                    "Text12":company.street or '',
                    "Text13":company.tambon_id.name or '',
                    "Text14":company.amphur_id.name or '',
                    "Text15":company.province_id.name or '',
                    "Text16":company.zip or '',
                    "Text17":company.phone or '',
                    "Text18":pnd.partner_id.name,
                    "Text19":pnd.partner_id.street or '',
                    "Text21":vouch.type_special is True and vouch.type_no or '',
                    "Text22":pnd.partner_id.nationality_id.name,
                    "Text25":int(pnd.line_ids[0].percent),
                    "Text46":vouch.attach_no,
                    "Num3":lang.format("%.2f",pnd.base_amount,grouping=True).replace(",","").replace("."," "),
                    "Num4":lang.format("%.2f",pnd.tax,grouping=True).replace(",","").replace("."," "),
                    # "Text51.4":lang.format("%.2f",vouch.add_amount,grouping=True).replace("."," "),
                    "Num6":lang.format("%.2f",pnd.tax,grouping=True).replace(",","").replace("."," "),
                    "Text55":"",
                    "Text54":"",
                    "Text26":day,
                    "Text27":month_sign,
                    "Text28":year_sign,
                    "'Check Box6'": section3,
                    "'Check Box8'": section65,
                    "'Check Box7'": section69,
                    "'Check Box36'": attachpnd,
                    "'Radio Button3'":int(vouch.type_of_income),
                    "'Radio Button2'":typepnd ,
                }

                pdf2=pdf_fill("wht_pnd54.pdf",vals)
                if pdf:
                    pdf = pdf_merge(pdf, pdf2)
                else:
                    pdf = pdf2

        return (pdf, "pdf")

report_custom("report.wht.pnd54")
