/** @odoo-module **/
import { registry } from "@web/core/registry";
import { LimitPrinting } from "./popup_limit_printing";

let iframeForReport;

function printPdf(url, callback) {
    let iframe = iframeForReport;
    if (!iframe) {
        iframe = iframeForReport = document.createElement('iframe');
        iframe.className = 'pdfIframe'
        document.body.appendChild(iframe);
        iframe.style.display = 'none';
        iframe.onload = function () {
            setTimeout(function () {
                iframe.focus();
                iframe.contentWindow.print();
                URL.revokeObjectURL(url)
                callback();
            }, 1);
        };
    }
    iframe.src = url;
}

function getReportUrl(action, type) {
    let url = `/report/${type}/${action.report_name}`;
    const actionContext = action.context || {};
    if (action.data && JSON.stringify(action.data) !== "{}") {
        const options = encodeURIComponent(JSON.stringify(action.data));
        const context = encodeURIComponent(JSON.stringify(actionContext));
        url += `?options=${options}&context=${context}`;
    } else {
        if (actionContext.active_ids) {
            url += `/${actionContext.active_ids.join(",")}`;
        }
        if (type === "html") {
            const context = encodeURIComponent(JSON.stringify(env.services.user.context));
            url += `?context=${context}`;
        }
    }
    return url;
}

let wkhtmltopdfStateProm;

registry
.category("ir.actions.report handlers")
    .add("limit_printing_handler", async function (action, options, env) {
        let { limit_printing_popup, limit_printing, print_option, print_count, access_right_id, print_report_name, state} = action;

        if ( access_right_id === "access_approved_manager" || state === "draft" || state === "sent" || state ==="cancel") {
            return false;
        }
        if (access_right_id === "access_approved_user" && print_count < limit_printing) {
            if (state !== "draft" || state !== "sent" || state !=="cancel") {
                let removeDialog;
                limit_printing_popup = await new Promise(resolve => {
                removeDialog = env.services.dialog.add(LimitPrinting, {
                  onSelectOption: (option) => {
                        return resolve(option);
                     },
                  print_count: print_count,
                  limit_printing: limit_printing,
                   },
                     {
                       onClose: () => {
                           return resolve('close');
                        }
                    });
                });
                await new Promise(resolve => {
                    removeDialog();
                    resolve();
                });

                if (limit_printing_popup === "close") {
                    return true;
                }
                const link = '<br><br><a href="http://wkhtmltopdf.org/" target="_blank">wkhtmltopdf.org</a>';

                if (!wkhtmltopdfStateProm) {
                    wkhtmltopdfStateProm = env.services.rpc("/report/check_wkhtmltopdf");
                }
                const state = await wkhtmltopdfStateProm;

                if (limit_printing_popup === "ok") {
                    const url = getReportUrl(action, "pdf");
                    if (print_option === "print") {
                        env.services.ui.block();
                        printPdf(url, () => {
                        env.services.ui.unblock();
                        });
    //                    setTimeout(() => {
    //                        window.location.reload();
    //                    }, 10000);

                    }
                    if (print_option === "open") {
                        window.open(url);
                    }

                    return true;
                } else {
                    return _executeReportClientAction(action, options);
                }
            }
        }

    });
