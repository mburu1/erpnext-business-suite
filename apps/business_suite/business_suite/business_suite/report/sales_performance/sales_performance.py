"""Sales Performance script report backed by ERPNext Sales Invoice."""

import frappe
from frappe import _


def execute(filters=None):
    filters = filters or {}
    invoice_filters = [["docstatus", "=", 1]]

    if filters.get("from_date"):
        invoice_filters.append(["posting_date", ">=", filters["from_date"]])
    if filters.get("to_date"):
        invoice_filters.append(["posting_date", "<=", filters["to_date"]])
    if filters.get("customer"):
        invoice_filters.append(["customer", "=", filters["customer"]])

    invoices = frappe.get_all(
        "Sales Invoice",
        filters=invoice_filters,
        fields=["customer", "grand_total"],
        limit_page_length=0,
    )

    totals = {}
    for invoice in invoices:
        customer = invoice.customer or _("Unknown")
        bucket = totals.setdefault(
            customer,
            {"invoice_count": 0, "net_total": 0, "avg_invoice": 0},
        )
        bucket["invoice_count"] += 1
        bucket["net_total"] += invoice.grand_total or 0

    for bucket in totals.values():
        bucket["avg_invoice"] = (
            bucket["net_total"] / bucket["invoice_count"]
            if bucket["invoice_count"]
            else 0
        )

    columns = [
        {"fieldname": "customer", "label": _("Customer"), "fieldtype": "Link", "options": "Customer", "width": 200},
        {"fieldname": "invoice_count", "label": _("Invoices"), "fieldtype": "Int", "width": 100},
        {"fieldname": "net_total", "label": _("Net Total"), "fieldtype": "Currency", "width": 130},
        {"fieldname": "avg_invoice", "label": _("Average Invoice"), "fieldtype": "Currency", "width": 140},
    ]
    data = [
        {"customer": customer, **values}
        for customer, values in sorted(
            totals.items(),
            key=lambda item: item[1]["net_total"],
            reverse=True,
        )
    ]
    return columns, data
