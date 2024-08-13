# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2012 Omar Castiñeira Saavedra <omar@pexego.es>
#                         Pexego Sistemas Informáticos http://www.pexego.es
# Copyright (C) 2013 Tadeus Prastowo <tadeus.prastowo@infi-nity.com>
#                         Vikasa Infinity Anugrah <http://www.infi-nity.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import base64
# import mbcs
import itertools
import odoo
from odoo import release
from odoo import api, fields, models
from odoo.tools.translate import _


class create_data_pnd(models.Model):
    _name = 'jasper.create.data.pnd'
    _description = 'Create data template PND'

    def action_create_xml(self):
        this = self.browse(self.ids)[0]
        if this.filename != False:
            raise osv.except_osv(('Error'), ('Create All Ready Please Click Download ',this.filename))
        pnd_id = self._context.get('active_ids', [])[0]
        pnd_obj = self.env['account.wht.pnd'].browse(pnd_id)
        if pnd_obj.pnd_type == 'pp7':
            filename = "PND53.txt"
        elif pnd_obj.pnd_type == 'pp54':
            filename = "PND54.txt"
        else:
            filename = "PND3.txt"
        self._cr.execute("""SELECT
                        TO_CHAR(
                            ROW_NUMBER ( ) OVER ( ORDER BY rp.DATE ),
                            'fm00000' 
                        ) AS ROW,
                        rp.vat AS pid,
                        rpt.NAME AS title,
                        ltrim(
                            rtrim(
                                ltrim( rtrim( rp.name, ' ' ), ' ' ),
                                '	' 
                            ),
                            '	' 
                        ) AS full_name,
                        TO_CHAR( tw.date_doc + INTERVAL '543 year', 'DD/MM/YYYY' ) AS DATE,
                        twl.note AS note,
                        twl.percent AS percent,
                        ROUND( twl.base_amount, 2 ) AS base,
                        ROUND(
                            twl.base_amount * ( twl.percent / 100 ),
                            2 
                        ) AS tax,
                        twl.TYPE AS CONDITION,
                        twl.wht_type_id as wht_type,
                        rp.street,
                        rp.street2 AS road,
                        COALESCE ( ' อ.' || rp.city, '' ) || COALESCE ( ' จ.' || rcs.NAME, '' ) || COALESCE ( ' ' || rp.zip, '' ) AS address2,
                        ltrim(
                            rtrim(
                                ltrim( rtrim( rp.NAME, ' ' ), ' ' ),
                                '	' 
                            ),
                            '	' 
                        ) AS company_name,
                        COALESCE ( rp.branch , '00000' ) AS branch 
                    FROM
                        account_wht_pnd twp
                        LEFT JOIN account_wht_pnds twps ON twps.pnd_id = twp.ID 
                        LEFT JOIN account_wht tw ON tw.ID = twps.wht_id
                        LEFT JOIN account_wht_line twl ON tw.ID = twl.wht_id
                        LEFT JOIN res_partner rp ON rp.ID = tw.partner_id
                        LEFT JOIN res_partner_title rpt ON rp.title = rpt.ID 
                        LEFT JOIN res_country_state rcs ON rcs.ID = rp.state_id
                        LEFT JOIN res_country rct ON rct.ID = rp.country_id
                    WHERE
                        twp.ID = %s
                    ORDER BY
                        DATE ASC,
                    ROW""", (pnd_id,))
        pnd_objs = self._cr.dictfetchall()
        xml = ""

        for pnd3 in pnd_objs:
            #Get Row number
            if pnd3['row']:
                xml += pnd3['row'] + "|"
            else:
                xml += "|"
            # Get ID
            if pnd3['pid']:
                xml += pnd3['pid'] + "|"
            else:
                xml += "|"

            #Check PND 53 get company_name
            if pnd_obj.pnd_type == 'pp7':
                #Get branch
                if pnd3['branch']:
                    xml += pnd3['branch'] + "|"
                else:
                    xml += "|"
                # Get Title
                if pnd3['title']:
                    xml += pnd3['title'] + "|"
                else:
                    xml += "|"
                #Get Company name
                if pnd3['company_name']:
                    xml += pnd3['company_name'] + "|"
                else:
                    xml += "|"
            else:
                #Check PND 3 get Name and LastName
                # Get Title
                if pnd3['title']:
                    xml += pnd3['title'] + "|"
                else:
                    xml += "|"
                if pnd3['full_name']:
                    xml += pnd3['full_name'] + "|"
                else:
                    xml += "|"

                if 'last_name' in pnd3 and pnd3['last_name']:
                    xml += pnd3['last_name'] + "|"
                else:
                    xml += "|"
            #Get Address
            lengths = [30,10,20,30,30,30,40,5]
            string = addr = ""
            if pnd3['street']:
                string += pnd3['street']
            # if pnd3['alley']:
            #     string += u' ซอย' + pnd3['alley']
            if pnd3['road']:
                string += u' ถนน' + pnd3['road']
            if pnd3['address2']:
                string += pnd3['address2'] + "|"
            else:
                string += "|"
            addr = '|'.join([string[sum(lengths[:i]):sum(lengths[:i + 1])] for i in range(len(lengths))])
            xml += addr
            # xml += string
            #Get Address Amphur Tambun Province
            # if pnd3[14]:
            #     xml += pnd3[14] + "|"
            # else:
            #     xml += "|"
            #Get Date WHT
            if pnd3['date']:
                xml += str(pnd3['date']) + "|"
            else:
                xml += "|"
            #Get Note WHT
            if pnd3['note']:
                xml += str(pnd3['note']) + "|"
            else:
                if pnd3['wht_type'] == 15:
                    xml += "ค่าบริการ" + "|"
                else:
                    xml += "|"
            #Get Percent
            if pnd3['percent']:
                xml += str(pnd3['percent']) + "|"
            else:
                xml += "|"
            #Get Base Tax
            if pnd3['base']:
                xml += str(pnd3['base']) + "|"
            else:
                xml += "|"
            #Get tax
            if pnd3['tax']:
                xml += str(pnd3['tax']) + "|"
            else:
                xml += "|"
            #Get Concition
            if pnd3['condition']:
                xml += str(pnd3['condition'])
            else:
                xml

            xml += "\r\n"

        asciidata = xml.encode("UTF-8", "ignore")

        self.write({
            'data': base64.encodebytes(asciidata),
            'filename': filename
        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'jasper.create.data.pnd',
            'view_mode': 'form',
            'res_id': this.id,
            'views': [(False, 'form')],
            'target': 'new',
        }

    company_id = fields.Many2one(string='Company', comodel_name='res.company', required=True,
                                 default=lambda self: self.env.company)
    filename = fields.Char('File Name', size=32)
    active_id = fields.Integer('Active ID')
    help = fields.Text(string='Positon PND3',readonly=True,default='0:Seq | 1:TaxID | 2:Title | 3:Name | 4:LastName | 5:Address  | 6:DateDoc | 7:Description | 8:Percent | 9:BaseAmount | 10:TaxAmount | 11:Condition')
    help_53 = fields.Text(string='Positon PND53', readonly=True,default='0:Seq | 1:TaxID | 2:Branch | 3:Title | 4:CompanyName | 5:Address  | 6:DateDoc | 7:Description | 8:Percent | 9:BaseAmount | 10:TaxAmount | 11:Condition')
    data = fields.Binary('Data')

