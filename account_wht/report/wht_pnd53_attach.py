# -*- encoding: utf-8 -*-
import odoo
from odoo import api, fields, models, _
from openerp.report.interface import report_int
import datetime
from report_tools import pdf_fill, pdf_merge
# from pdf_tools import pdf_fill,pdf_merge

from num2word import num2word_th, fmt_tin, fmt_addr, fmt_new_addr,fmt_thaidate
from bahttext import bahttext


class report_custom(report_int):
    def create(self, cr, uid, ids, datas, context=None):
        env = odoo.api.Environment(cr, uid, context or {})
        #print "WHT PND3 Attach Report"
        lang = env['res.lang'].browse([1])
        user = env['res.users'].browse([1])
        pdf = False
        pdf2 = False
        vouch = env['account.wht.pnd'].browse(ids)
        company = vouch.company_id        
        
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
        sup_name = {}
        sup_address = {}
        sup_address2 = {}
        wht_date = {}
        wht_name_line = {}
        wht_percent_line = {}
        wht_base_amount = {}
        wht_tax_line = {}
        vals = {}
        amount = {}
        vat_amount = {}
        branch={}
        
        count_line = vouch.attach_count
        pages = 1
        for line in vouch.wht_ids:
            k += 1
            no[i] = k
            vat[i] = line.partner_id.number and fmt_tin(line.partner_id.number) or ""
            sup_name[i] = line.partner_id.name
            sup_address[i] = fmt_new_addr(line.partner_id)
            branch[i] = line.partner_id.branch or "00000"
            # province = line.partner_id.state_id and line.partner_id.state_id.name or ""
            # sup_address[i]= (line.partner_id.street or "") +"  "+ (line.partner_id.street2 or "")
            # sup_address2[i]= (line.partner_id.city or "")  +"  "+ (province or "")
            for wht_line in line.line_ids:
                wht_date[j] = line.date_doc and fmt_thaidate(line.date_doc) or ""                
                pnd_type_str = wht_line.wht_type_id.display_name
                if wht_line.wht_type_id.id == 15 and wht_line.note:
                    pnd_type_str+' '+wht_line.note
                elif wht_line.wht_type_id.id == 15 and not wht_line.note:
                    pnd_type_str + ' ' + 'ค่าบริการ'
                wht_name_line[j] = pnd_type_str
                wht_percent_line[j] = wht_line.percent
                wht_base_amount[j] = wht_line.base_amount
                wht_tax_line[j] =   wht_line.tax
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
                    "Text42":  company.vat and fmt_tin(company.vat) or "",
                    "Text30":  company.partner_id.branch or "00000",
                    "Text31":   pages,
                    "Text32":   vouch.attach_no,
                    "Text46":  "",
                    "Text47": "",#company.tr_position and company.tr_position or "",
                    # "Text48":   day,
                    # "Text49":"    "+ str(month+1),
                    # "Text50":   year,
                    "Text48": "",
                    "Text49": "",
                    "Text50": "",
                    "Text44":  lang.format("%.2f",amount[pages],grouping=True).replace("."," "),
                    "Text45": lang.format("%.2f", vat_amount[pages],grouping=True).replace("."," "),
#                    "Text44":  lang.format("%.2f",vouch.total_amount,grouping=True).replace("."," "),
#                    "Text45":  lang.format("%.2f", vouch.total_tax_send,grouping=True).replace("."," "),
                    "Text33.0.0": no.has_key(1) and no[1] or "",
                    "Text33.0.1": no.has_key(2) and no[2] or "",
                    "Text33.0.2": no.has_key(3) and no[3] or "",
                    "Text33.0.3": no.has_key(4) and no[4] or "",
                    "Text33.0.4": no.has_key(5) and no[5] or "",
                    "Text33.0.5": no.has_key(6) and no[6] or "",
                    "Text13.0": vat.has_key(1) and vat[1] or "",
                    "Text13.1": vat.has_key(2) and vat[2] or "",
                    "Text13.2": vat.has_key(3) and vat[3] or "",
                    "Text13.3": vat.has_key(4) and vat[4] or "",
                    "Text13.4": vat.has_key(5) and vat[5] or "",
                    "Text13.5": vat.has_key(6) and vat[6] or "",
                    "Text14.0": branch.has_key(1) and branch[1] or "",
                    "Text14.1": branch.has_key(2) and branch[2] or "",
                    "Text14.2": branch.has_key(3) and branch[3] or "",
                    "Text14.3": branch.has_key(4) and branch[4] or "",
                    "Text14.4": branch.has_key(5) and branch[5] or "",
                    "Text14.5": branch.has_key(6) and branch[6] or "",
                    "Text16.0": sup_name.has_key(1) and sup_name[1] or "",
                    "Text16.1": sup_name.has_key(2) and sup_name[2] or "",
                    "Text16.2": sup_name.has_key(3) and sup_name[3] or "",
                    "Text16.3": sup_name.has_key(4) and sup_name[4] or "",
                    "Text16.4": sup_name.has_key(5) and sup_name[5] or "",
                    "Text16.5": sup_name.has_key(6) and sup_name[6] or "",
                    "Text17.0": sup_address.has_key(1) and sup_address[1] or "",
                    "Text17.1": sup_address.has_key(2) and sup_address[2] or "",
                    "Text17.2": sup_address.has_key(3) and sup_address[3] or "",
                    "Text17.3": sup_address.has_key(4) and sup_address[4] or "",
                    "Text17.4": sup_address.has_key(5) and sup_address[5] or "",
                    "Text17.5": sup_address.has_key(6) and sup_address[6] or "",   
                    "Text18.0": sup_address2.has_key(1) and sup_address2[1] or "",
                    "Text18.1": sup_address2.has_key(2) and sup_address2[2] or "",
                    "Text18.2": sup_address2.has_key(3) and sup_address2[3] or "",
                    "Text18.3": sup_address2.has_key(4) and sup_address2[4] or "",
                    "Text18.4": sup_address2.has_key(5) and sup_address2[5] or "",
                    "Text18.5": sup_address2.has_key(6) and sup_address2[6] or "",                                               
                    "Text19.0": wht_date.has_key(1) and wht_date[1] or "",
                    "Text25.0": wht_date.has_key(2) and wht_date[2] or "",
                    "Text36.0": wht_date.has_key(3) and wht_date[3] or "",
                    "Text19.1": wht_date.has_key(4) and wht_date[4] or "",
                    "Text25.1": wht_date.has_key(5) and wht_date[5] or "",
                    "Text36.1": wht_date.has_key(6) and wht_date[6] or "",
                    "Text19.2": wht_date.has_key(7) and wht_date[7] or "",
                    "Text25.2": wht_date.has_key(8) and wht_date[8] or "",            
                    "Text36.2": wht_date.has_key(9) and wht_date[9] or "",   
                    "Text19.3": wht_date.has_key(10) and wht_date[10] or "",  
                    "Text25.3": wht_date.has_key(11) and wht_date[11] or "",              
                    "Text36.3": wht_date.has_key(12) and wht_date[12] or "",
                    "Text19.4": wht_date.has_key(13) and wht_date[13] or "",
                    "Text25.4": wht_date.has_key(14) and wht_date[14] or "",                       
                    "Text36.4": wht_date.has_key(15) and wht_date[15] or "",                
                    "Text19.5": wht_date.has_key(16) and wht_date[16] or "",                  
                    "Text25.5": wht_date.has_key(17) and wht_date[17] or "",      
                    "Text36.5": wht_date.has_key(18) and wht_date[18] or "",                                          
                    "Text20.0": wht_name_line.has_key(1) and wht_name_line[1] or "",
                    "Text26.0": wht_name_line.has_key(2) and wht_name_line[2] or "",
                    "Text37.0": wht_name_line.has_key(3) and wht_name_line[3] or "",
                    "Text20.1": wht_name_line.has_key(4) and wht_name_line[4] or "",
                    "Text26.1": wht_name_line.has_key(5) and wht_name_line[5] or "",
                    "Text37.1": wht_name_line.has_key(6) and wht_name_line[6] or "",
                    "Text20.2": wht_name_line.has_key(7) and wht_name_line[7] or "",
                    "Text26.2": wht_name_line.has_key(8) and wht_name_line[8] or "",
                    "Text37.2": wht_name_line.has_key(9) and wht_name_line[9] or "",  
                    "Text20.3": wht_name_line.has_key(10) and wht_name_line[10] or "",      
                    "Text26.3": wht_name_line.has_key(11) and wht_name_line[11] or "", 
                    "Text37.3": wht_name_line.has_key(12) and wht_name_line[12] or "",      
                    "Text20.4": wht_name_line.has_key(13) and wht_name_line[13] or "", 
                    "Text26.4": wht_name_line.has_key(14) and wht_name_line[14] or "", 
                    "Text37.4": wht_name_line.has_key(15) and wht_name_line[15] or "",                    
                    "Text20.5": wht_name_line.has_key(16) and wht_name_line[16] or "", 
                    "Text26.5": wht_name_line.has_key(17) and wht_name_line[17] or "", 
                    "Text37.5": wht_name_line.has_key(18) and wht_name_line[18] or "",                                                                     
                    "Text21.0": wht_percent_line.has_key(1) and wht_percent_line[1] or "",
                    "Text27.0": wht_percent_line.has_key(2) and wht_percent_line[2] or "",
                    "Text38.0": wht_percent_line.has_key(3) and wht_percent_line[3] or "" ,
                    "Text21.1": wht_percent_line.has_key(4) and wht_percent_line[4] or "" ,
                    "Text27.1": wht_percent_line.has_key(5) and wht_percent_line[5] or "" ,
                    "Text38.1": wht_percent_line.has_key(6) and wht_percent_line[6] or "" ,
                    "Text21.2": wht_percent_line.has_key(7) and wht_percent_line[7] or "" ,
                    "Text27.2": wht_percent_line.has_key(8) and wht_percent_line[8] or "" ,
                    "Text38.2": wht_percent_line.has_key(9) and wht_percent_line[9] or "" ,
                    "Text21.3": wht_percent_line.has_key(10) and wht_percent_line[10] or "" ,
                    "Text27.3": wht_percent_line.has_key(11) and wht_percent_line[11] or "" ,
                    "Text38.3": wht_percent_line.has_key(12) and wht_percent_line[12] or "" ,
                    "Text21.4": wht_percent_line.has_key(13) and wht_percent_line[13] or "" ,
                    "Text27.4": wht_percent_line.has_key(14) and wht_percent_line[14] or "" ,
                    "Text38.4": wht_percent_line.has_key(15) and wht_percent_line[15] or "" ,
                    "Text21.5": wht_percent_line.has_key(16) and wht_percent_line[16] or "" ,
                    "Text27.5": wht_percent_line.has_key(17) and wht_percent_line[17] or "" ,
                    "Text38.5": wht_percent_line.has_key(18) and wht_percent_line[18] or "" ,      
                    "Text22.0": wht_base_amount.has_key(1) and wht_base_amount[1] and lang.format("%.2f",wht_base_amount[1],grouping=True).replace("."," ") or "",
                    "Text28.0": wht_base_amount.has_key(2) and wht_base_amount[2] and lang.format("%.2f",wht_base_amount[2],grouping=True).replace("."," ") or "",
                    "Text39.0": wht_base_amount.has_key(3) and wht_base_amount[3] and lang.format("%.2f",wht_base_amount[3],grouping=True).replace("."," ") or "",
                    "Text22.1": wht_base_amount.has_key(4) and wht_base_amount[4] and lang.format("%.2f",wht_base_amount[4],grouping=True).replace("."," ") or "",
                    "Text28.1": wht_base_amount.has_key(5) and wht_base_amount[5] and lang.format("%.2f",wht_base_amount[5],grouping=True).replace("."," ") or "",
                    "Text39.1": wht_base_amount.has_key(6) and wht_base_amount[6] and lang.format("%.2f",wht_base_amount[6],grouping=True).replace("."," ") or "",
                    "Text22.2": wht_base_amount.has_key(7) and wht_base_amount[7] and lang.format("%.2f",wht_base_amount[7],grouping=True).replace("."," ") or "",
                    "Text28.2": wht_base_amount.has_key(8) and wht_base_amount[8] and lang.format("%.2f",wht_base_amount[8],grouping=True).replace("."," ") or "",
                    "Text39.2": wht_base_amount.has_key(9) and wht_base_amount[9]  and lang.format("%.2f",wht_base_amount[9],grouping=True).replace("."," ") or "",
                    "Text22.3": wht_base_amount.has_key(10) and wht_base_amount[10]  and lang.format("%.2f",wht_base_amount[10],grouping=True).replace("."," ") or "",
                    "Text28.3": wht_base_amount.has_key(11) and wht_base_amount[11] and lang.format("%.2f",wht_base_amount[11],grouping=True).replace("."," ") or "",
                    "Text39.3": wht_base_amount.has_key(12) and wht_base_amount[12] and lang.format("%.2f",wht_base_amount[12],grouping=True).replace("."," ") or "",
                    "Text22.4": wht_base_amount.has_key(13) and wht_base_amount[13] and lang.format("%.2f",wht_base_amount[13],grouping=True).replace("."," ") or "",
                    "Text28.4": wht_base_amount.has_key(14) and wht_base_amount[14] and lang.format("%.2f",wht_base_amount[14],grouping=True).replace("."," ") or "",
                    "Text39.4": wht_base_amount.has_key(15) and wht_base_amount[15] and lang.format("%.2f",wht_base_amount[15],grouping=True).replace("."," ") or "",
                    "Text22.5": wht_base_amount.has_key(16) and wht_base_amount[16] and lang.format("%.2f",wht_base_amount[16],grouping=True).replace("."," ") or "",
                    "Text28.5": wht_base_amount.has_key(17) and wht_base_amount[17] and lang.format("%.2f",wht_base_amount[17],grouping=True).replace("."," ") or "",
                    "Text39.5": wht_base_amount.has_key(18) and wht_base_amount[18] and lang.format("%.2f",wht_base_amount[18],grouping=True).replace("."," ") or "",
                    "Text23.0": wht_tax_line.has_key(1) and wht_tax_line[1] and lang.format("%.2f",wht_tax_line[1],grouping=True).replace("."," ") or "",
                    "Text34.0": wht_tax_line.has_key(2) and wht_tax_line[2] and lang.format("%.2f",wht_tax_line[2],grouping=True).replace("."," ") or "",
                    "Text40.0": wht_tax_line.has_key(3) and wht_tax_line[3] and lang.format("%.2f",wht_tax_line[3],grouping=True).replace("."," ") or "",
                    "Text23.1": wht_tax_line.has_key(4) and wht_tax_line[4] and lang.format("%.2f",wht_tax_line[4],grouping=True).replace("."," ") or "",
                    "Text34.1": wht_tax_line.has_key(5) and wht_tax_line[5] and lang.format("%.2f",wht_tax_line[5],grouping=True).replace("."," ") or "",
                    "Text40.1": wht_tax_line.has_key(6) and wht_tax_line[6] and lang.format("%.2f",wht_tax_line[6],grouping=True).replace("."," ") or "",
                    "Text23.2": wht_tax_line.has_key(7) and wht_tax_line[7] and lang.format("%.2f",wht_tax_line[7],grouping=True).replace("."," ") or "",
                    "Text34.2": wht_tax_line.has_key(8) and wht_tax_line[8] and lang.format("%.2f",wht_tax_line[8],grouping=True).replace("."," ") or "",
                    "Text40.2": wht_tax_line.has_key(9) and wht_tax_line[9] and lang.format("%.2f",wht_tax_line[9],grouping=True).replace("."," ") or "",
                    "Text23.3": wht_tax_line.has_key(10) and wht_tax_line[10] and lang.format("%.2f",wht_tax_line[10],grouping=True).replace("."," ") or "",
                    "Text34.3": wht_tax_line.has_key(11) and wht_tax_line[11] and lang.format("%.2f",wht_tax_line[11],grouping=True).replace("."," ") or "",
                    "Text40.3": wht_tax_line.has_key(12) and wht_tax_line[12] and lang.format("%.2f",wht_tax_line[12],grouping=True).replace("."," ") or "",
                    "Text23.4": wht_tax_line.has_key(13) and wht_tax_line[13] and lang.format("%.2f",wht_tax_line[13],grouping=True).replace("."," ") or "",
                    "Text34.4": wht_tax_line.has_key(14) and wht_tax_line[14] and lang.format("%.2f",wht_tax_line[14],grouping=True).replace("."," ") or "",
                    "Text40.4": wht_tax_line.has_key(15) and wht_tax_line[15] and lang.format("%.2f",wht_tax_line[15],grouping=True).replace("."," ") or "",
                    "Text23.5": wht_tax_line.has_key(16) and wht_tax_line[16] and lang.format("%.2f",wht_tax_line[16],grouping=True).replace("."," ") or "",
                    "Text34.5": wht_tax_line.has_key(17) and wht_tax_line[17] and lang.format("%.2f",wht_tax_line[17],grouping=True).replace("."," ") or "",
                    "Text40.5": wht_tax_line.has_key(18) and wht_tax_line[18] and lang.format("%.2f",wht_tax_line[18],grouping=True).replace("."," ") or "",
                }
            if k == count_line:              
                pdf2 = pdf_fill("wht_pnd53_attach.pdf",vals)
                if pdf:
                    pdf = pdf_merge(pdf, pdf2)
                else:
                    pdf = pdf2
            elif i == 7:       
                pdf2 = pdf_fill("wht_pnd53_attach.pdf",vals)
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
                    sup_address[ii]= ""
                    sup_address2[ii]= ""
                for jrnge in range(18):
                    jj += 1
                    wht_date[jj] =  False
                    wht_name_line[jj] = False
                    wht_percent_line[jj] = False
                    wht_base_amount[jj] = False
                    wht_tax_line[jj] = False

        return (pdf, "pdf")
    
report_custom("report.wht.pnd53.attach")
