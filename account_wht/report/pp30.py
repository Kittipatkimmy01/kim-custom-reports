# -*- encoding: utf-8 -*-
import odoo
from odoo import api, fields, models, _
from openerp.report.interface import report_int
from report_tools import pdf_fill, pdf_merge

from num2word import num2word_th, fmt_tin
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
            company = vouch.company_id
            
            yearnow=int(vouch.date_pp30[0:4]) + 543
            monthnow=int(vouch.date_pp30[5:7])
            daynow=int(vouch.date_pp30[8:10])
                            
#             daynow = datetime.datetime.now().day
#             monthnow  = datetime.datetime.now().month
#             yearnow = int(datetime.datetime.now().year)+543
                        
                
            sale_untax = vouch.sale_amount_untaxed - vouch.sale_refund_amount_untaxed + (vouch.sale_receipt_amount_untaxed - vouch.sale_receipt_amount_tax)
            sale_tax = vouch.sale_amount_tax - vouch.sale_refund_amount_tax + vouch.sale_receipt_amount_tax
            purchase_untax = vouch.purchase_amount_untaxed - vouch.purchase_refund_amount_untaxed + (vouch.purchase_receipt_amount_untaxed - vouch.purchase_receipt_amount_tax)
            purchase_tax = vouch.purchase_amount_tax - vouch.purchase_refund_amount_tax + vouch.purchase_receipt_amount_tax
            
    
            vals={
                "Text1":company.tr_tax and fmt_tin(company.tr_tax) or "",
                "Text57":company.tr_branch or '',
                "name_place":company.tr_company_name,                
                "number":company.tr_building or '',
                "room_no":company.tr_room_no or '',
                "floor":company.tr_class or '',
                "village":company.tr_village or '',
                "add_no":company.tr_no or '',
                "moo":company.tr_moo or '',
                "soi":company.tr_alley or '',
                "road":company.tr_road or '',
                "district":company.tr_district or '',
                "amphur":company.tr_amphoe or '',
                "province":company.tr_province or '',
                "Text58":company.tr_zip or '',
                "tel":company.tr_phone or '',
                "year":yearnow,
                "Text53":lang.format("%.2f",sale_untax,grouping=True).replace("."," "),
                "Text47":lang.format("%.2f",sale_untax,grouping=True).replace("."," "),
                "Text30":lang.format("%.2f",sale_tax,grouping=True).replace("."," "),
                "Text51":lang.format("%.2f",purchase_untax,grouping=True).replace("."," "),
                "Text52":lang.format("%.2f",purchase_tax,grouping=True).replace("."," "),       
                "signature4": company.tr_name or '',
                "date":str(daynow)+"/"+ str(monthnow)+"/"+ str(yearnow),   
              
            }
            if sale_tax >= purchase_tax:
                vat = sale_tax - purchase_tax
                vals.update({
                             "Text34":lang.format("%.2f",vat,grouping=True).replace("."," "),
                             "Text38":lang.format("%.2f",vat,grouping=True).replace("."," "), 
                             "'Check Box11'": "Yes",
                             })
            else:
                vat = purchase_tax - sale_tax
                vals.update({
                             "Text35":lang.format("%.2f",vat,grouping=True).replace("."," "),
                             "Text39":lang.format("%.2f",vat,grouping=True).replace("."," "), 
                             "'Check Box12'": "Yes",
                             })                

            pdf2=pdf_fill("pp30.pdf",vals)
            if pdf:
                pdf = pdf_merge(pdf, pdf2)
            else:
                pdf = pdf2
                
        return (pdf, "pdf")

report_custom("report.pp30")
