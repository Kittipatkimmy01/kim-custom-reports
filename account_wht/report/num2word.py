#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime
sym={
    "en": {
        "spc": " ",
        "0": "zero",
        "x": ["one","two","three","four","five" ,"six","seven","eight","nine"],
        "1x": ["ten","eleven","twelve","thirteen","fourteen","fifteen","sixteen","seventeen","eighteen","nineteen"],
        "x0": ["twenty","thirty","fourty","fifty","sixty","seventy","eighty","ninety"],
        "100": "hundred",
        "1K": "thousand",
        "1M": "million",
    },
    "th": {
        "spc": "",
        "0": "ศูนย์",
        "x": ["หนึ่ง","สอง","สาม","สี่","ห้า" ,"หก","เจ็ด","แปด","เก้า"],
        "x0": ["สิบ","ยี่สิบ","สามสิบ","สี่สิบ","ห้าสิบ","หกสิบ","เจ็ดสิบ","แปดสิบ","เก้าสิบ"],
        "x1": "เอ็ด",
        "100": "ร้อย",
        "1K": "พัน",
        "10K": "หมื่น",
        "100K": "แสน",
        "1M":"ล้าน",
    }
}

def num2word(n,l="en"):
    if n==0:
        return sym[l]["0"] + " "
    elif n<10:
        return sym[l]["x"][n-1]
    elif n<100:
        if l=="en":
            if n<20:
                return sym[l]["1x"][n-10]
            else:
                return sym[l]["x0"][n/10-2]+(n%10 and sym[l]["spc"]+num2word(n%10,l) or "")
        elif l=="th":
            return sym[l]["x0"][n/10-1]+(n%10 and (n%10==1 and sym[l]["x1"] or sym[l]["x"][n%10-1]) or "")
    elif n<1000:
        return sym[l]["x"][n/100-1]+sym[l]["spc"]+sym[l]["100"]+(n%100 and sym[l]["spc"]+num2word(n%100,l) or "")
    elif n<1000000:
        if l=="en":
            return num2word(n/1000,l)+sym[l]["spc"]+sym[l]["1K"]+(n%1000 and sym[l]["spc"]+num2word(n%1000,l) or "")
        elif l=="th":
            if n<10000:
                return sym[l]["x"][n/1000-1]+sym[l]["1K"]+(n%1000 and num2word(n%1000,l) or "")
            elif n<100000:
                return sym[l]["x"][n/10000-1]+sym[l]["10K"]+(n%1000 and num2word(n%10000,l) or "")
            else:
                return sym[l]["x"][n/100000-1]+sym[l]["100K"]+(n%10000 and num2word(n%100000,l) or "")
    elif n<1000000000:
        return num2word(n/1000000,l)+sym[l]["spc"]+sym[l]["1M"]+sym[l]["spc"]+(n%1000000 and num2word(n%1000000,l) or "")
    else:
        return "N/A"

def num2word_th(n,l="th"):
    base=0
    end=0
    number = n
    if type(n) == type(''):
        number=float(n)
    word = ''
    if type(number) in (type(0),type(0.0)):
        number = ('%.2f'%number).split('.')
        base = num2word(int(number[0]),l=l)
        #print number
        if int(number[1])!=0:
            end = num2word(int(number[1]),l=l)
        if base==0 and end==0:
            word='ศุนย์บาทถ้วน'
        if base!=0 and end==0:
            word=base+'บาทถ้วน'
        if base!=0 and end!=0:
            word=base+'บาท'+end+'สตางค์'
    return word

if __name__ == '__main__':
    import sys
    n=sys.stdin.readline()
    print(num2word_th(n))

def fmt_tin(tin):
    if len(str(tin)) >= 13:
        return " %s    %s   %s   %s  %s     %s   %s  %s  %s  %s     %s  %s     %s"%(tin[0],tin[1],tin[2],tin[3],tin[4],tin[5],tin[6],tin[7],tin[8],tin[9],tin[10],tin[11],tin[12])
    else:
        return tin

def fmt_tin_pnd54(tin):
    if len(str(tin)) >= 13:
        return " %s   %s %s %s %s   %s %s %s %s %s   %s %s   %s"%(tin[0],tin[1],tin[2],tin[3],tin[4],tin[5],tin[6],tin[7],tin[8],tin[9],tin[10],tin[11],tin[12])
    else:
        return tin

def set_satang(vals):
    for key in vals.keys():
        if key.startswith("tax"):
            amt=vals[key]
            vals[key]=int(amt)
            vals[key.replace("tax","st")]=int(amt*100.0)%100

def fmt_thaidate(date):
    dt=datetime.datetime.strptime(date,"%Y-%m-%d")
    return "%2d/%d/%d"%(dt.day,dt.month,dt.year+543)

def fmt_addr(addr):
    s=""
    if addr.street:
        s+=addr.street
    if addr.street2:
        s+=" "+addr.street2
    if addr.city:
        s+=" "+addr.city
    if addr.state_id:
        s+=" "+addr.state_id.name
    if addr.zip:
        s+=" "+addr.zip
    return s

def fmt_new_addr(addr):
    s=""
    if addr.street:
        s+=addr.street
    if addr.street2:
        s+=" "+addr.street2
    if addr.city:
        s+=" "+addr.city
    if addr.state_id:
        s+=" "+addr.state_id.name
    if addr.zip:
        s+=" "+addr.zip
    return s

# def fmt_new_addr(addr):
#     s=""
#     if addr.street:
#         s+=addr.street
#     if addr.moo:
#         s+=u" หมู่ "+addr.moo
#     if addr.alley:
#         s+=u" ซ. "+addr.alley
#     if addr.street2:
#         s+=u" ถนน."+addr.street2
#     if addr.tambon_id:
#         if addr.province_id.name_eng == 'Bangkok':
#             s += u" แขวง. "+addr.tambon_id.name
#         else:
#             s += u" ต. " + addr.tambon_id.name
#     if addr.amphur_id:
#         if addr.province_id.name_eng == 'Bangkok':
#             s += u" เขต. "+addr.amphur_id.name
#         else:
#             s += u" อ. " + addr.amphur_id.name
#     if addr.province_id:
#         if addr.province_id.name_eng == 'Bangkok':
#             s += u" " + addr.province_id.name
#         else:
#             s+=u" จ. "+addr.province_id.name
#     if addr.zip:
#         s+=" "+addr.zip
#     return s
