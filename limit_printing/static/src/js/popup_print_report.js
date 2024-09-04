/** @odoo-module */
import { _lt } from "@web/core/l10n/translation";
import { Dialog } from "@web/core/dialog/dialog";
import { Component } from "@odoo/owl";

export class PrintReportPopup extends Component { }
PrintReportPopup.components = { Dialog }
PrintReportPopup.template = "limit_printing.print_report_dialog";
