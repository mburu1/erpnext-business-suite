frappe.query_reports["Customer Activity"] = {
    filters: [
        {
            fieldname: "customer",
            label: __("Customer"),
            fieldtype: "Link",
            options: "Customer"
        },
        {
            fieldname: "onboarding_status",
            label: __("Onboarding Status"),
            fieldtype: "Select",
            options: "\nDraft\nVerification\nApproved\nActive"
        }
    ]
};
