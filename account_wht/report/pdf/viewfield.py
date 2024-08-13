import sys
from pdfminer.pdfparser import PDFParser, PDFDocument
from pdfminer.pdftypes import resolve1

filename = sys.argv[1]
fp = open(filename, 'rb')

parser = PDFParser(fp)
doc = PDFDocument()
parser.set_document(doc)
doc.set_parser(parser)
doc.initialize()

fields = resolve1(doc.catalog['AcroForm'])['Fields']
field_lists = {}
for i in fields:
    field = resolve1(i)
    name, value = field.get('T'), field.get('V')
    field_lists[name] = value
    #print '{0}: {1}'.format(name, value)
field_key = field_lists.keys()
field_key.sort() 
new_list = {}
for key in sorted(field_lists.iterkeys()):
    new_list[key] = field_lists[key]
    print '%s:%s' % (key, field_lists[key])
#print new_list
