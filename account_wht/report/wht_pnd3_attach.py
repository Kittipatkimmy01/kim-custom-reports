# -*- encoding: utf-8 -*-
import odoo
from odoo import api, fields, models, _
from openerp.report.interface import report_int
from report_tools import pdf_fill, pdf_merge
# from openerp.osv import fields, osv

# import openerp.pooler
from num2word import num2word_th, fmt_thaidate, fmt_tin, fmt_addr,fmt_new_addr
import datetime

class report_custom(report_int):
    def create(self,cr,uid,ids,datas,context={}):
        env = odoo.api.Environment(cr, uid, context or {})
        #print "WHT PND3 Attach Report"
        lang = env['res.lang'].browse([1])
        user = env['res.users'].browse([1])
        pdf = False        
        pdf2 = False
        vouch = env['account.wht.pnd'].browse(ids)
        company = vouch.company_id.partner_id
        
        year=int(vouch.date_pnd[0:4])+543
        month=int(vouch.date_pnd[5:7]) - 1

        day=int(vouch.date_pnd[8:10])
                        
        daynow = datetime.datetime.now().day
        monthnow  = datetime.datetime.now().month
        yearnow = int(datetime.datetime.now().year)+543

        
        i = 1
        j = 1
        k = 0
        no = {}
        vat = {}
        branch = {}
        sup_name = {}
        sup_last_name = {}
        sup_address = {}
        wht_date = {}
        wht_name_line = {}
        wht_percent_line = {}
        wht_base_amount = {}
        wht_tax_line = {}
        vals = {}
        amount = {}
        vat_amount = {}
        
        count_line = vouch.attach_count
        pages = total_pages = 1
        per_page = divmod(count_line,6)
        if per_page[0] > 0:
            if per_page[1] > 0:
                total_pages = per_page[0] + 1
        for line in vouch.wht_ids:
            k += 1
            no[i] = k
            vat[i] = line.partner_id.number and fmt_tin(line.partner_id.number) or ""
            branch[i] = line.partner_id.tax_detail or "0001"
            last_name_split = []
            last_name_split = line.partner_id.last_name.split()
            sup_name[i] = line.partner_id.first_name+last_name_split[0] if len(last_name_split) >= 2 else line.partner_id.first_name
            sup_last_name[i] = last_name_split[1] if len(last_name_split) >= 2 else line.partner_id.last_name

            # province = line.partner_id.state_id and line.partner_id.state_id.name or ""
            # sup_address[i]= (line.partner_id.street or "") + " " + (line.partner_id.street2 or "") + " "+ (line.partner_id.city or "") + " " + (province or "")
            sup_address[i] = fmt_new_addr(line.partner_id)
            for wht_line in line.line_ids:
                wht_name = ""
                if u'6 อื่นๆ (ระบุ)' in wht_line.wht_type_id.display_name:
                    if wht_line.note:
                        wht_name += wht_line.wht_type_id.display_name + ' ' +wht_line.note
                    else:
                        wht_name += u'ค่าบริการ'
                else:
                    wht_name += wht_line.wht_type_id.display_name
                wht_date[j] = line.date_doc and fmt_thaidate(line.date_doc) or ""
                wht_name_line[j] = wht_name
                wht_percent_line[j] = wht_line.percent
                wht_base_amount[j] = wht_line.base_amount
                wht_tax_line[j] = wht_line.tax
                if amount.has_key(pages) and amount[pages]:
                    amount[pages] = amount[pages] + wht_line.base_amount
                else:
                    amount[pages] = wht_line.base_amount
                if vat_amount.has_key(pages) and vat_amount[pages]:
                    vat_amount[pages] = vat_amount[pages] + wht_line.tax
                else:
                    vat_amount[pages] = wht_line.tax
                j += 1 
            j = (3 * i) + 1
            i += 1

            vals={
                    "Text2.0":  company.vat and fmt_tin(company.vat) or "",
                    "Text4":    company.branch or "00000",
                    "Text18":   pages,
                    # "Text19":   vouch.attach_no,
                    "Text19": total_pages,
                    "Text21":"      "+ (""),
                    "Text22":"        "+ (""),
                    # "Text23":   day,
                    # "Text24":"    "+ str(month+1),
                    # "Text25":   year,
                    "Text23": "",
                    "Text24": "",
                    "Text25": "",
                    "Text9.7":  lang.format("%.2f",amount[pages],grouping=True).replace("."," "),
                    "Text10.7": lang.format("%.2f", vat_amount[pages],grouping=True).replace("."," "),
#                    "Text9.7":  lang.format("%.2f",vouch.total_amount,grouping=True).replace("."," "),
#                    "Text10.7": lang.format("%.2f", vouch.total_tax_send,grouping=True).replace("."," "),
                    "Text20.0.0":       no.has_key(1) and no[1] or "",
                    "Text20.1.0":       no.has_key(2) and no[2] or "",
                    "Text20.2.0":       no.has_key(3) and no[3] or "",
                    "Text20.3.0":       no.has_key(4) and no[4] or "",
                    "Text20.4.0":       no.has_key(5) and no[5] or "",
                    "Text20.5.0":       no.has_key(6) and no[6] or "",
                    "Text2.1":          vat.has_key(1) and vat[1] or "",
                    "Text2.2":          vat.has_key(2) and vat[2] or "",
                    "Text2.3":          vat.has_key(3) and vat[3] or "",
                    "Text2.4":          vat.has_key(4) and vat[4] or "",
                    "Text2.5":          vat.has_key(5) and vat[5] or "",
                    "Text2.6":          vat.has_key(6) and vat[6] or "",

                "Text5.1": branch.has_key(1) and branch[1] or "",
                "Text5.2": branch.has_key(2) and branch[2] or "",
                "Text5.3": branch.has_key(3) and branch[3] or "",
                "Text5.4": branch.has_key(4) and branch[4] or "",
                "Text5.5": branch.has_key(5) and branch[5] or "",
                "Text5.6": branch.has_key(6) and branch[6] or "",
                    "Text6.0":          sup_name.has_key(1) and sup_name[1] or "",
                    "Text6.1":          sup_name.has_key(2) and sup_name[2] or "",
                    "Text6.2":          sup_name.has_key(3) and sup_name[3] or "",
                    "Text6.3":          sup_name.has_key(4) and sup_name[4] or "",
                    "Text6.4":          sup_name.has_key(5) and sup_name[5] or "",
                    "Text6.5":          sup_name.has_key(6) and sup_name[6] or "",
                "Text7.0": sup_last_name.has_key(1) and sup_last_name[1] or "",
                "Text7.1": sup_last_name.has_key(2) and sup_last_name[2] or "",
                "Text7.2": sup_last_name.has_key(3) and sup_last_name[3] or "",
                "Text7.3": sup_last_name.has_key(4) and sup_last_name[4] or "",
                "Text7.4": sup_last_name.has_key(5) and sup_last_name[5] or "",
                "Text7.5": sup_last_name.has_key(6) and sup_last_name[6] or "",
                    "Text8.0":          sup_address.has_key(1) and sup_address[1] or "",
                    "Text8.1":          sup_address.has_key(2) and sup_address[2] or "",
                    "Text8.2":          sup_address.has_key(3) and sup_address[3] or "",
                    "Text8.3":          sup_address.has_key(4) and sup_address[4] or "",
                    "Text8.4":          sup_address.has_key(5) and sup_address[5] or "",
                    "Text8.5":          sup_address.has_key(6) and sup_address[6] or "",            
                    "Text1.0.0":        wht_date.has_key(1) and wht_date[1] or "",
                    "Text1.0.1.0":      wht_date.has_key(2) and wht_date[2] or "",
                    "Text1.0.1.1.0":    wht_date.has_key(3) and wht_date[3] or "",
                    "Text1.0.1.1.1.0":  wht_date.has_key(4) and wht_date[4] or "",
                    "Text1.0.1.1.1.1":  wht_date.has_key(5) and wht_date[5] or "",
                    "Text1.1.0":        wht_date.has_key(6) and wht_date[6] or "",
                    "Text1.1.1.0":      wht_date.has_key(7) and wht_date[7] or "",
                    "Text1.1.1.1":      wht_date.has_key(8) and wht_date[8] or "",            
                    "Text1.2.0":        wht_date.has_key(9) and wht_date[9] or "",   
                    "Text1.2.1.0":      wht_date.has_key(10) and wht_date[10] or "",  
                    "Text1.2.1.1":      wht_date.has_key(11) and wht_date[11] or "",              
                    "Text1.3.0":        wht_date.has_key(12) and wht_date[12] or "",
                    "Text1.3.1.0":      wht_date.has_key(13) and wht_date[13] or "",
                    "Text1.3.1.1":      wht_date.has_key(14) and wht_date[14] or "",                       
                    "Text1.4.0":        wht_date.has_key(15) and wht_date[15] or "",                
                    "Text1.4.1.0":      wht_date.has_key(16) and wht_date[16] or "",                  
                    "Text1.4.1.1":      wht_date.has_key(17) and wht_date[17] or "",      
                    "Text1.5":          wht_date.has_key(18) and wht_date[18] or "",                                          
                    "Text12.0.0":       wht_name_line.has_key(1) and wht_name_line[1] or "",
                    "Text12.0.1.0":     wht_name_line.has_key(2) and wht_name_line[2] or "",
                    "Text12.0.1.1.0":   wht_name_line.has_key(3) and wht_name_line[3] or "",
                    "Text12.0.1.1.1.0": wht_name_line.has_key(4) and wht_name_line[4] or "",
                    "Text12.0.1.1.1.1": wht_name_line.has_key(5) and wht_name_line[5] or "",
                    "Text12.1.0":       wht_name_line.has_key(6) and wht_name_line[6] or "",
                    "Text12.1.1.0":     wht_name_line.has_key(7) and wht_name_line[7] or "",
                    "Text12.1.1.1":     wht_name_line.has_key(8) and wht_name_line[8] or "",
                    "Text12.2.0":       wht_name_line.has_key(9) and wht_name_line[9] or "",  
                    "Text12.2.1.0":     wht_name_line.has_key(10) and wht_name_line[10] or "",      
                    "Text12.2.1.1":     wht_name_line.has_key(11) and wht_name_line[11] or "", 
                    "Text12.3.0":       wht_name_line.has_key(12) and wht_name_line[12] or "",      
                    "Text12.3.1.0":     wht_name_line.has_key(13) and wht_name_line[13] or "", 
                    "Text12.3.1.1":     wht_name_line.has_key(14) and wht_name_line[14] or "", 
                    "Text12.4.0":       wht_name_line.has_key(15) and wht_name_line[15] or "",                    
                    "Text12.4.1.0":     wht_name_line.has_key(16) and wht_name_line[16] or "", 
                    "Text12.4.1.1":     wht_name_line.has_key(17) and wht_name_line[17] or "", 
                    "Text12.5":         wht_name_line.has_key(18) and wht_name_line[18] or "",                                                                     
                    "Text5.0.0":        wht_percent_line.has_key(1) and wht_percent_line[1] or "",
                    "Text5.0.1.0":      wht_percent_line.has_key(2) and wht_percent_line[2] or "",
                    "Text5.0.1.1.0":    wht_percent_line.has_key(3) and wht_percent_line[3] or "" ,
                    "Text5.0.1.1.1.0":  wht_percent_line.has_key(4) and wht_percent_line[4] or "" ,
                    "Text5.0.1.1.1.1":  wht_percent_line.has_key(5) and wht_percent_line[5] or "" ,
                    "Text5.1.0":        wht_percent_line.has_key(6) and wht_percent_line[6] or "" ,
                    "Text5.1.1.0":      wht_percent_line.has_key(7) and wht_percent_line[7] or "" ,
                    "Text5.1.1.1":      wht_percent_line.has_key(8) and wht_percent_line[8] or "" ,
                    "Text5.2.0":        wht_percent_line.has_key(9) and wht_percent_line[9] or "" ,
                    "Text5.2.1.0":      wht_percent_line.has_key(10) and wht_percent_line[10] or "" ,
                    "Text5.2.1.1":      wht_percent_line.has_key(11) and wht_percent_line[11] or "" ,
                    "Text5.3.0":        wht_percent_line.has_key(12) and wht_percent_line[12] or "" ,
                    "Text5.3.1.0":      wht_percent_line.has_key(13) and wht_percent_line[13] or "" ,
                    "Text5.3.1.1":      wht_percent_line.has_key(14) and wht_percent_line[14] or "" ,
                    "Text5.4.0":        wht_percent_line.has_key(15) and wht_percent_line[15] or "" ,
                    "Text5.4.1.0":      wht_percent_line.has_key(16) and wht_percent_line[16] or "" ,
                    "Text5.4.1.1":      wht_percent_line.has_key(17) and wht_percent_line[17] or "" ,
                    "Text5.5":          wht_percent_line.has_key(18) and wht_percent_line[18] or "" ,      
                    "Text9.0.0":        wht_base_amount.has_key(1) and wht_base_amount[1] and lang.format("%.2f",wht_base_amount[1],grouping=True).replace("."," ") or "",
                    "Text9.0.1.0":      wht_base_amount.has_key(2) and wht_base_amount[2] and lang.format("%.2f",wht_base_amount[2],grouping=True).replace("."," ") or "",
                    "Text9.0.1.1.0":    wht_base_amount.has_key(3) and wht_base_amount[3] and lang.format("%.2f",wht_base_amount[3],grouping=True).replace("."," ") or "",
                    "Text9.0.1.1.1.0":  wht_base_amount.has_key(4) and wht_base_amount[4] and lang.format("%.2f",wht_base_amount[4],grouping=True).replace("."," ") or "",
                    "Text9.0.1.1.1.1":  wht_base_amount.has_key(5) and wht_base_amount[5] and lang.format("%.2f",wht_base_amount[5],grouping=True).replace("."," ") or "",
                    "Text9.1.0":        wht_base_amount.has_key(6) and wht_base_amount[6] and lang.format("%.2f",wht_base_amount[6],grouping=True).replace("."," ") or "",
                    "Text9.1.1.0":      wht_base_amount.has_key(7) and wht_base_amount[7] and lang.format("%.2f",wht_base_amount[7],grouping=True).replace("."," ") or "",
                    "Text9.1.1.1":      wht_base_amount.has_key(8) and wht_base_amount[8] and lang.format("%.2f",wht_base_amount[8],grouping=True).replace("."," ") or "",
                    "Text9.2.0":        wht_base_amount.has_key(9) and wht_base_amount[9]  and lang.format("%.2f",wht_base_amount[9],grouping=True).replace("."," ") or "",
                    "Text9.2.1.0":      wht_base_amount.has_key(10) and wht_base_amount[10]  and lang.format("%.2f",wht_base_amount[10],grouping=True).replace("."," ") or "",
                    "Text9.2.1.1":      wht_base_amount.has_key(11) and wht_base_amount[11] and lang.format("%.2f",wht_base_amount[11],grouping=True).replace("."," ") or "",
                    "Text9.3.0":        wht_base_amount.has_key(12) and wht_base_amount[12] and lang.format("%.2f",wht_base_amount[12],grouping=True).replace("."," ") or "",
                    "Text9.3.1.0":      wht_base_amount.has_key(13) and wht_base_amount[13] and lang.format("%.2f",wht_base_amount[13],grouping=True).replace("."," ") or "",
                    "Text9.3.1.1":      wht_base_amount.has_key(14) and wht_base_amount[14] and lang.format("%.2f",wht_base_amount[14],grouping=True).replace("."," ") or "",
                    "Text9.4.0":        wht_base_amount.has_key(15) and wht_base_amount[15] and lang.format("%.2f",wht_base_amount[15],grouping=True).replace("."," ") or "",
                    "Text9.4.1.0":      wht_base_amount.has_key(16) and wht_base_amount[16] and lang.format("%.2f",wht_base_amount[16],grouping=True).replace("."," ") or "",
                    "Text9.4.1.1":      wht_base_amount.has_key(17) and wht_base_amount[17] and lang.format("%.2f",wht_base_amount[17],grouping=True).replace("."," ") or "",
                    "Text9.5":          wht_base_amount.has_key(18) and wht_base_amount[18] and lang.format("%.2f",wht_base_amount[18],grouping=True).replace("."," ") or "",
                    "Text10.0.0":       wht_tax_line.has_key(1) and wht_tax_line[1] and lang.format("%.2f",wht_tax_line[1],grouping=True).replace("."," ") or "",
                    "Text10.0.1.0":     wht_tax_line.has_key(2) and wht_tax_line[2] and lang.format("%.2f",wht_tax_line[2],grouping=True).replace("."," ") or "",
                    "Text10.0.1.1.0":   wht_tax_line.has_key(3) and wht_tax_line[3] and lang.format("%.2f",wht_tax_line[3],grouping=True).replace("."," ") or "",
                    "Text10.0.1.1.1.0": wht_tax_line.has_key(4) and wht_tax_line[4] and lang.format("%.2f",wht_tax_line[4],grouping=True).replace("."," ") or "",
                    "Text10.0.1.1.1.1": wht_tax_line.has_key(5) and wht_tax_line[5] and lang.format("%.2f",wht_tax_line[5],grouping=True).replace("."," ") or "",
                    "Text10.1.0":       wht_tax_line.has_key(6) and wht_tax_line[6] and lang.format("%.2f",wht_tax_line[6],grouping=True).replace("."," ") or "",
                    "Text10.1.1.0":     wht_tax_line.has_key(7) and wht_tax_line[7] and lang.format("%.2f",wht_tax_line[7],grouping=True).replace("."," ") or "",
                    "Text10.1.1.1":     wht_tax_line.has_key(8) and wht_tax_line[8] and lang.format("%.2f",wht_tax_line[8],grouping=True).replace("."," ") or "",
                    "Text10.2.0":       wht_tax_line.has_key(9) and wht_tax_line[9] and lang.format("%.2f",wht_tax_line[9],grouping=True).replace("."," ") or "",
                    "Text10.2.1.0":     wht_tax_line.has_key(10) and wht_tax_line[10] and lang.format("%.2f",wht_tax_line[10],grouping=True).replace("."," ") or "",
                    "Text10.2.1.1":     wht_tax_line.has_key(11) and wht_tax_line[11] and lang.format("%.2f",wht_tax_line[11],grouping=True).replace("."," ") or "",
                    "Text10.3.0":       wht_tax_line.has_key(12) and wht_tax_line[12] and lang.format("%.2f",wht_tax_line[12],grouping=True).replace("."," ") or "",
                    "Text10.3.1.0":     wht_tax_line.has_key(13) and wht_tax_line[13] and lang.format("%.2f",wht_tax_line[13],grouping=True).replace("."," ") or "",
                    "Text10.3.1.1":     wht_tax_line.has_key(14) and wht_tax_line[14] and lang.format("%.2f",wht_tax_line[14],grouping=True).replace("."," ") or "",
                    "Text10.4.0":       wht_tax_line.has_key(15) and wht_tax_line[15] and lang.format("%.2f",wht_tax_line[15],grouping=True).replace("."," ") or "",
                    "Text10.4.1.0":     wht_tax_line.has_key(16) and wht_tax_line[16] and lang.format("%.2f",wht_tax_line[16],grouping=True).replace("."," ") or "",
                    "Text10.4.1.1":     wht_tax_line.has_key(17) and wht_tax_line[17] and lang.format("%.2f",wht_tax_line[17],grouping=True).replace("."," ") or "",
                    "Text10.5":         wht_tax_line.has_key(18) and wht_tax_line[18] and lang.format("%.2f",wht_tax_line[18],grouping=True).replace("."," ") or "",
                }
            if k == count_line:              
                pdf2 = pdf_fill("wht_pnd3_attach.pdf",vals)
                if pdf:
                    pdf = pdf_merge(pdf, pdf2)
                else:
                    pdf = pdf2
            elif i == 7:       
                pdf2 = pdf_fill("wht_pnd3_attach.pdf",vals)
                pages += 1
                i = 1
                j = 1
                ii = 0
                jj = 0
                if pdf:
                    pdf = pdf_merge(pdf, pdf2)
                else:
                    pdf = pdf2
                for irnge in range(6):
                    ii += 1 
                    no[ii] = ""
                    vat[ii] = ""
                    sup_name[ii] = ""
                    sup_last_name[ii]=""
                    sup_address[ii]= ""
                for jrnge in range(18):
                    jj += 1
                    wht_date[jj] =  False
                    wht_name_line[jj] = False
                    wht_percent_line[jj] = False
                    wht_base_amount[jj] = False
                    wht_tax_line[jj] = False

        return (pdf, "pdf")
    
report_custom("report.wht.pnd3.attach")
