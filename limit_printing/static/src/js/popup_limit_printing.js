/** @odoo-module */
import { _lt } from "@web/core/l10n/translation";
import { Dialog } from "@web/core/dialog/dialog";

const { Component } = owl;

export class LimitPrinting extends Component { }

LimitPrinting.components = { Dialog }
LimitPrinting.template = "limit_printing.limit_printing_dialog";