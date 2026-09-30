frappe.query_reports["Inventory Summary"] = {
    filters: [
        {
            fieldname: "active",
            label: __("Active"),
            fieldtype: "Select",
            options: "\n1\n0",
            default: "1"
        },
        {
            fieldname: "warehouse",
            label: __("Warehouse"),
            fieldtype: "Link",
            options: "Warehouse"
        }
    ]
};
