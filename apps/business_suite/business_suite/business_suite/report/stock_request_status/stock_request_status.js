frappe.query_reports["Stock Request Status"] = {
    filters: [
        {
            fieldname: "status",
            label: __("Status"),
            fieldtype: "Select",
            options: "\nDraft\nSubmitted\nManager Review\nApproved\nFulfilled\nClosed"
        },
        {
            fieldname: "priority",
            label: __("Priority"),
            fieldtype: "Select",
            options: "\nLow\nMedium\nHigh"
        },
        {
            fieldname: "warehouse",
            label: __("Warehouse"),
            fieldtype: "Link",
            options: "Warehouse"
        }
    ]
};
