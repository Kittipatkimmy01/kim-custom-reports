#!/usr/bin/env jython

import sys
#sys.path.append("/usr/share/java/itextpdf-5.4.1.jar")
sys.path.append("itextpdf-5.4.1.jar")
#sys.path.append("/usr/share/java/itext-2.0.7.jar")
#sys.path.append("/usr/share/java/xercesImpl.jar")
#sys.path.append("/usr/share/java/xml-apis.jar")

from java.io import FileOutputStream
from com.itextpdf.text.pdf import PdfReader,PdfStamper,BaseFont
#from com.lowagie.text.pdf import PdfReader,PdfStamper,BaseFont
#import re
import time
#import xmlrpclib
from SimpleXMLRPCServer import SimpleXMLRPCServer

def pdf_fill(orig_pdf,new_pdf,vals):
    #print "pdf_fill",orig_pdf,new_pdf,vals
    t0=time.time()
    #print orig_pdf
    rd=PdfReader(orig_pdf)
    #print new_pdf
    #print t0
    st=PdfStamper(rd,FileOutputStream(new_pdf))
    font=BaseFont.createFont("Garuda.ttf",BaseFont.IDENTITY_H,BaseFont.EMBEDDED)
    form=st.getAcroFields()
    for k,v in vals.items():
        try:
            form.setFieldProperty(k,"textfont",font,None)
            form.setField(k,v.decode('utf-8'))
        except Exception,e:
            raise Exception("Field %s: %s"%(k,str(e)))
    st.setFormFlattening(True)
    st.close()
    t1=time.time()
    #print "finished in %.2fs"%(t1-t0)
    return True

def pdf_merge(pdf1,pdf2):
    #print "pdf_merge",orig_pdf,vals
    t0=time.time()
    pdf=pdf1
    t1=time.time()
    #print "finished in %.2fs"%(t1-t0)
    return pdf

serv=SimpleXMLRPCServer(("localhost",9999))
serv.register_function(pdf_fill,"pdf_fill")
serv.register_function(pdf_merge,"pdf_merge")
print "waiting for requests..."
serv.serve_forever()
