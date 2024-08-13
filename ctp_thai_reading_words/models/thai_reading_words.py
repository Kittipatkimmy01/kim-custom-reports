# -*- coding: utf-8 -*-
from odoo import api, models, _

class ThaiReadingWords(models.TransientModel):
    _name = "thai.reading.words"
    _description = "baht text"

    @api.model
    def thai_month(self, month):
        "แปลงตัวเลขเดือนเป็นตัวหนังสือภาษาไทย"
        month = int(month)
        if month:
            month_arr = [u"มกราคม", u"กุมภาพันธ์", u"มีนาคม", u"เมษายน", u"พฤษภาคม", u"มิถุนายน", u"กรกฎาคม", u"สิงหาคม", u"กันยายน", u"ตุลาคม", u"พฤศจิกายน", u"ธันวาคม"];
            return month_arr[month-1]

    def unit_process(self, val):
        thai_number = [u"ศูนย์", u"หนึ่ง", u"สอง", u"สาม", u"สี่", u"ห้า", u"หก", u"เจ็ด", u"แปด", u"เก้า"]
        unit = [u"", u"สิบ", u"ร้อย", u"พัน", u"หมื่น", u"แสน", u"ล้าน"]
        length = len(val) > 1
        result = ""

        for index, current in enumerate(map(int, val)):
            if current:
                if index:
                    result = unit[index] + result
                if length and current == 1 and index == 0:
                    result += u"เอ็ด"
                elif index == 1 and current == 2:
                    result = u"ยี่" + result
                elif index != 1 or current != 1:
                    result = thai_number[current] + result

        return result

    def thai_num2text(self, number):
        "แปลงตัวเลขเป็นตัวหนังสือภาษาไทย"
        sn = str(number)[::-1]
        nl = [sn[i:i + 6].rstrip("0") for i in range(0, len(sn), 6)]
        result = self.unit_process(nl.pop(0))

        for i in nl:
            result = self.unit_process(i) + "ล้าน" + result

        return result

    def thai_baht(self, nb):
        "function แบ่งตัวเลขออกเป็น 2 กลุ่ม"
        split_num = str(nb).split(".")
        int_part = int(split_num[0])
        decimal_part = int(split_num[1])

        result = self.thai_num2text(int_part) + "บาท"

        if decimal_part > 0:
            result += self.thai_num2text(decimal_part) + "สตางค์"
        else:
            result += "ถ้วน"

        return result
