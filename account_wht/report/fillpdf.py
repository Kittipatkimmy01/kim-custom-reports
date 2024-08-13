#!/usr/bin/env jython
# -*- encoding: utf-8 -*-

import sys
sys.path.append("/usr/share/java/itextpdf-5.4.1.jar")
#sys.path.append("itextpdf-5.4.1.jar")

from java.io import FileOutputStream
from com.itextpdf.text.pdf import PdfReader,PdfStamper,BaseFont
import time


def pdf_fill(orig_pdf,new_pdf,vals):
    t0=time.time()
    rd=PdfReader(orig_pdf)
    st=PdfStamper(rd,FileOutputStream(new_pdf))
    font=BaseFont.createFont("Garuda.ttf",BaseFont.IDENTITY_H,BaseFont.EMBEDDED)
    form=st.getAcroFields()
    for k,v in vals.items():
        try:
            form.setFieldProperty(k,"textfont",font,None)
            form.setField(k,v)
        except Exception,e:
            raise Exception("Field %s: %s"%(k,str(e)))
    st.setFormFlattening(True)
    st.close()
    t1=time.time()
    print "finished in %.2fs"%(t1-t0)
    return True

new_data = dict(arg.split('=') for arg in sys.argv[3:])
pdf_fill(sys.argv[1],
         sys.argv[2],
         new_data)

