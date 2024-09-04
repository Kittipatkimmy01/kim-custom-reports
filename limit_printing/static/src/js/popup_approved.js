/** @odoo-module */
import { _lt } from "@web/core/l10n/translation";
import { Dialog } from "@web/core/dialog/dialog";

const { Component } = owl;

export class ApprovedPopup extends Component { }

ApprovedPopup.components = { Dialog }
ApprovedPopup.template = "limit_printing.approved_dialog";