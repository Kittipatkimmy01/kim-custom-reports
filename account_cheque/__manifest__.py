# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Trinity Roots co.,ltd. (<http://www.trinityroots.co.th>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


{
    "name" : "Accounting - Cheque",
    "version" : "17.0",
    "depends" : ["base","account","account_payment_method"],
    "author" : "Cybernetics+",
    "category": "Accounting",
    "description": """
    * Cheque
    """,
    "website": "http://www.cybernetics.plus",
    "data": [
        "security/ir.model.access.csv",
        "security/cheque.xml",
        "views/account_journal_view.xml",
        "views/cheque_view.xml",
#         "views/account_payment_mode_view.xml",
#         "views/cheque_report.xml",
        "data/cheque_data.xml",
    ],
    "demo": [],
    "license": "LGPL-3",
    "installable": True,
    "auto_install": False,
    "images": ["images/icon.png"],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
