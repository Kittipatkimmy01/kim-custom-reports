# -*- encoding: utf-8 -*-
import os
import tempfile
import PyPDF2
from io import BytesIO
# from fillpdf import fillpdfs
from datetime import datetime,timedelta
import logging

_logger = logging.getLogger(__name__)

def safe_unicode(obj, *args):
    """ return the unicode representation of obj """
    try:
        return unicode(obj, *args)
    except UnicodeDecodeError:
        ascii_text = str(obj).encode('string_escape')
        return unicode(ascii_text)

def safe_str(obj):
    """ return the byte string representation of obj """
    try:
        return str(obj)
    except UnicodeEncodeError:
        return unicode(obj).encode('utf-8')

def decode_vals(vals): #need to format for str and unicode object-
    dc={}
    for k,v in vals.items():
#         k,v = unicode(k),safe_unicode(v) # key and value must the same type str,str
        dc[k]=v
    return dc

# def pdf_fill(orig_pdf, vals):
#     #sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
#     path_root = str(os.path.dirname(os.path.abspath(__file__)))
#     vals=decode_vals(vals)
#     #orig_pdf_abs=os.path.join(os.getcwd(),orig_pdf)
#     orig_pdf_abs= path_root + '/pdf/' + orig_pdf
#     tmp = tempfile.NamedTemporaryFile()
#     print('filling pdf : ',orig_pdf,tmp,vals)
#     #jy_serv.pdf_fill(orig_pdf_abs,tmp,vals)
#     arg = ''
#     for key in vals.keys():
#         arg = arg + "%s='%s' " % (key, vals[key])
#     arg = arg.encode('utf-8')
#     print(">>",path_root)
#     #cmd = "jython %s/module_accounting/tr_thai_account/report/fillpdf.py %s %s %s" % (os.getcwd(), orig_pdf_abs, tmp, arg)
#     #cmd = "jython home/cash/workspace/acct/module_accounting/tr_standard_account/report/fillpdf.py %s %s %s" % (orig_pdf_abs, tmp, arg)
#     cmd = "jython %s/fillpdf.py %s %s %s" % (path_root, orig_pdf_abs, tmp, arg)
# #     print(cmd)
# #     os.system(cmd)
# #     fp = BytesIO()
# #     pdf = tmp.read()

#     fielf_pdf = fillpdfs.get_form_fields(orig_pdf_abs)
    
#     new_pdf_path = path_root + '/pdf/'
    
#     fillpdfs.write_fillable_pdf(orig_pdf_abs, new_pdf_path + 'new.pdf', vals, flatten=True)
    
#     final_file_path = new_pdf_path + 'new.pdf'
#     file_read = open(final_file_path, 'rb')
#     pdf = file_read.read()
#     os.unlink(final_file_path)
#     return pdf

def pdf_fill(orig_pdf, vals):
    return True
    #sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    path_root = str(os.path.dirname(os.path.abspath(__file__)))
    vals=decode_vals(vals)
    #orig_pdf_abs=os.path.join(os.getcwd(),orig_pdf)
    orig_pdf_abs= path_root + '/pdf/' + orig_pdf
    # orig_pdf_abs= orig_pdf
    tmp = tempfile.NamedTemporaryFile()
    arg = ''
    for key in vals.keys():
        arg = arg + "%s='%s' " % (key, vals[key])
    arg = arg.encode('utf-8')
    # print(">>",path_root)
    #cmd = "jython %s/module_accounting/tr_thai_account/report/fillpdf.py %s %s %s" % (os.getcwd(), orig_pdf_abs, tmp, arg)
    #cmd = "jython home/cash/workspace/acct/module_accounting/tr_standard_account/report/fillpdf.py %s %s %s" % (orig_pdf_abs, tmp, arg)
    # cmd = "jython %s/fillpdf.py %s %s %s" % ('', orig_pdf_abs, tmp, arg)
#     print(cmd)
#     os.system(cmd)
#     fp = BytesIO()
#     pdf = tmp.read()

    fielf_pdf = fillpdfs.get_form_fields(orig_pdf_abs)
    # new_pdf_path = path_root + '/pdf/'
    new_pdf_path = ''
        
    select_date = datetime.now().strftime('%Y%m%d%H%M%S')
    # filename = "wht_" + select_date + ".pdf"
    filename = path_root + "wht_" + select_date + ".pdf"
    
    _logger.warning(vals)  # debug
    
    fillpdfs.write_fillable_pdf(orig_pdf_abs, filename, vals, flatten=True)
    
    final_file_path = filename
    file_read = open(final_file_path, 'rb')
    pdf = file_read.read()
    os.unlink(final_file_path)
    return pdf


def pdf_merge(pdf1, pdf2):
    try:
        tmp1=tempfile.NamedTemporaryFile()
        tmp2=tempfile.NamedTemporaryFile()
        tmp3=tempfile.NamedTemporaryFile()
        output = PyPDF2.PdfFileWriter()
        file(tmp1,"w").write(pdf1)
        file(tmp2,"w").write(pdf2)
        input1 = PyPDF2.PdfFileReader(file(tmp1, "rb"))
        input2 = PyPDF2.PdfFileReader(file(tmp2, "rb"))
        for page in range(input1.getNumPages()):
            output.addPage(input1.getPage(page))
        for page in range(input2.getNumPages()):
            output.addPage(input2.getPage(page))
        outputStream = file(tmp3, "wb")
        output.write(outputStream)
        outputStream.close()
        pdf3=tmp3.read()
        os.unlink(tmp1)
        os.unlink(tmp2)
        os.unlink(tmp3)
        return pdf3
    except:
        raise Exception("Failed to merge PDF files")
