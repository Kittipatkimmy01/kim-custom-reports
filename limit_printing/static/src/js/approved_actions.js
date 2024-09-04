///** @odoo-module **/
//import { registry } from "@web/core/registry";
//import { ApprovedPopup } from "./popup_approved";
//
//registry
//.category("ir.actions.report handlers")
//    .add("approved_popup_handler", async function (action, options, env) {
//    let { approved_popup, limit_printing, print_option, print_count, default_print_option, access_right_id } = action;
//    const print_id = action.context.active_id;
//    if (access_right_id === "access_approved_manager"){
//        return false;
//    }
//
//    if (access_right_id === "access_approved_user") {
//        let removeDialog;
//        approved_popup = await new Promise(resolve => {
//            removeDialog = env.services.dialog.add(ApprovedPopup, {
//                onSelectOption: (option) => {
//                    return resolve(option);
//                }
//            }, {
//                onClose: () => {
//                    return resolve('close');
//                }
//            });
//        });
//        await new Promise(resolve => {
//           removeDialog();
//           resolve();
//        });
//
//        if (approved_popup === "close") {
//            return true;
//        }
//
//        if (approved_popup === "ok") {
//            return await rpc.query({
//                    model: "ir.actions.report",
//                    method: "reset_print_count",
//                    args: [print_id],
//                });
//        }
//
//        if (default_print_option === "download") {
//                return false;
//        }
//
//
//    }
//});