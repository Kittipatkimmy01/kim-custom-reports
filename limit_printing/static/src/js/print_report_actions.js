/** @odoo-module **/
import { registry } from "@web/core/registry";
import { PrintReportPopup } from "./popup_print_report";

registry
.category("ir.actions.report handlers")
    .add("print_report_popup_handler", async function (action, options, env) {
    let { print_report_popup, limit_printing, print_option, print_count, default_print_option, access_right_id, state} = action;
    const user_id = action.context.uid;

    if (access_right_id === "access_approved_manager" || state === "draft" || state === "sent" || state ==="cancel") {
        return false;
    }

    if (access_right_id === "access_approved_user" && print_count > limit_printing) {
        let removeDialog;
        print_report_popup = await new Promise(resolve => {
            removeDialog = env.services.dialog.add(PrintReportPopup, {
                onSelectOption: (option) => {
                    return resolve(option);
                }
            }, {
                onClose: () => {
                    return resolve('close');
                }
            });
        });
        await new Promise(resolve => {
           removeDialog();
           resolve();
        });

        if (print_report_popup === "close") {
            return true;
        }

        if (print_report_popup === "request_approve") {
            env.services.rpc("/request_to_approve", {
            args: [user_id, options],
            kwargs: {},
            method: "request_to_approve",
            model: "approval.request",
        }).then(() => {
            window.location.reload();
        });
        }

//        if (default_print_option === "download") {
//                return false;
//        }
    }
});


