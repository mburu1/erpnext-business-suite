frappe.query_reports["Integration Summary"] = {
    filters: [
        {
            fieldname: "integration_name",
            label: __("Integration"),
            fieldtype: "Data"
        },
        {
            fieldname: "direction",
            label: __("Direction"),
            fieldtype: "Select",
            options: "\nInbound\nOutbound"
        },
        {
            fieldname: "status",
            label: __("Status"),
            fieldtype: "Select",
            options: "\nQueued\nProcessing\nCompleted\nFailed"
        }
    ]
};
