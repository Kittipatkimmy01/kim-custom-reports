# -*- encoding: utf-8 -*-
import odoo
from odoo import api, fields, models, _
from openerp.report.interface import report_int
from report_tools import pdf_fill, pdf_merge
# from openerp.osv import fields, osv

# import openerp.pooler
from num2word import num2word_th, fmt_tin, set_satang, fmt_thaidate
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
            print ('>>',vouch.date_pnd)
            # company = vouch.company_id.partner_id
            wht_partner_id = env['ir.values'].get_default('account.config.wht', 'partner_wht_id',
                company_id=env.user.company_id.id)
            company = env['res.partner'].browse(wht_partner_id)
            
            year=int(vouch.date_pnd[0:4])+543
            #month=int(vouch.date_pnd[5:7]) - 1
            #month=int(vouch.date_pnd[5:7]) - 2
            month=int(vouch.date_pnd[5:7]) - 1
            month_sign = int(vouch.date_pnd[5:7])
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

            day=int(vouch.date_pnd[8:10])
                            
            daynow = datetime.datetime.now().day
            monthnow  = datetime.datetime.now().month 
            yearnow = int(datetime.datetime.now().year)+543
                   
            typepnd = 0
            section3 = ""
            section48 = ""
            section50 = ""
            attachpnd = ""
            
            if vouch.type_normal == True:
                typepnd = 0
            else:
                typepnd = 1
            if  vouch.section_3 == True:
                section3 = "Yes"
            if  vouch.section_48 == True:
                section48 = "Yes"
            if  vouch.section_50 == True:
                section50 = "Yes"        
            if  vouch.attach_pnd == True:
                attachpnd = "Yes"             

            vals={
                "Text2":company.number and fmt_tin(company.number.strip()) or "",
                "Text3": company.tax_detail or '',
                "Text4":company.branch or '00000',
                "Text5":company.company_id.rml_header1,
                "Text6":company.building or '',
                "Text7":company.room_no or '',
                "Text8":company.floor or '',
                "Text9":'-',
                "Text10":company.house_no or '',
                "Text11":company.moo or '',
                "Text12":company.alley or '',
                "Text13":company.street or '',
                "Text14":company.tambon_id.name or '',
                "Text15":company.amphur_id.name or '',
                "Text16":company.province_id.name or '',
                "Text17":company.zip or '',
                "Text18":company.phone or '',
                "Text19":vouch.attach_count,
                "Text21": vouch.type_special is True and vouch.type_no or '',
                "Text22":year,
                "Text46":vouch.attach_no,
                "Text51.2":lang.format("%.2f",vouch.total_amount,grouping=True).replace("."," "),
                "Text51.3":lang.format("%.2f",vouch.total_tax,grouping=True).replace("."," "),
                "Text51.4":lang.format("%.2f",vouch.add_amount,grouping=True).replace("."," "),
                "Text51.5":lang.format("%.2f",vouch.total_tax_send,grouping=True).replace("."," "),
                "Text55":"",
                "Text54":"",
                # "Text56":day,
                "Text56": "",
                # "Text57":"    "+ str(month_sign),
                "Text57": "",
                # "Text58":yearnow,
                "Text58": "",
                "'Check Box6'": section3,
                "'Check Box7'": section48,
                "'Check Box8'": section50,
                "'Check Box36'": attachpnd,
                "'Radio Button23'": month_radio ,
                "'Radio Button19'":typepnd ,
            }
            #may = 0, #june = 4
    
            pdf2=pdf_fill("wht_pnd3.pdf",vals)
            if pdf:
                pdf = pdf_merge(pdf, pdf2)
            else:
                pdf = pdf2
                
        return (pdf, "pdf")

report_custom("report.wht.pnd3")
