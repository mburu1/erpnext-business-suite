"""Stock Request Status script report."""

import frappe
from frappe import _


def execute(filters=None):
    filters = filters or {}
    request_filters = {}

    if filters.get("status"):
        request_filters["status"] = filters["status"]
    if filters.get("priority"):
        request_filters["priority"] = filters["priority"]
    if filters.get("warehouse"):
        request_filters["warehouse"] = filters["warehouse"]

    columns = [
        {"fieldname": "status", "label": _("Status"), "fieldtype": "Data", "width": 140},
        {"fieldname": "priority", "label": _("Priority"), "fieldtype": "Data", "width": 100},
        {"fieldname": "warehouse", "label": _("Warehouse"), "fieldtype": "Link", "options": "Warehouse", "width": 180},
        {"fieldname": "request_count", "label": _("Requests"), "fieldtype": "Int", "width": 100},
    ]

    rows = frappe.get_all(
        "Stock Request",
        filters=request_filters,
        fields=["status", "priority", "warehouse"],
        limit_page_length=0,
    )

    buckets = {}
    for row in rows:
        key = (
            row.status or _("Unspecified"),
            row.priority or _("Unspecified"),
            row.warehouse or _("Unspecified"),
        )
        buckets[key] = buckets.get(key, 0) + 1

    data = [
        {
            "status": status,
            "priority": priority,
            "warehouse": warehouse,
            "request_count": count,
        }
        for (status, priority, warehouse), count in sorted(
            buckets.items(),
            key=lambda item: (-item[1], item[0]),
        )
    ]

    return columns, data
