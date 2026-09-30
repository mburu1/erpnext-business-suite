"""Integration Summary script report."""

import frappe
from frappe import _


def execute(filters=None):
    filters = filters or {}
    log_filters = {}

    if filters.get("integration_name"):
        log_filters["integration_name"] = filters["integration_name"]
    if filters.get("status"):
        log_filters["status"] = filters["status"]
    if filters.get("direction"):
        log_filters["direction"] = filters["direction"]

    columns = [
        {"fieldname": "integration_name", "label": _("Integration"), "fieldtype": "Data", "width": 180},
        {"fieldname": "direction", "label": _("Direction"), "fieldtype": "Data", "width": 100},
        {"fieldname": "status", "label": _("Status"), "fieldtype": "Data", "width": 120},
        {"fieldname": "request_count", "label": _("Requests"), "fieldtype": "Int", "width": 100},
        {"fieldname": "failed_count", "label": _("Failed"), "fieldtype": "Int", "width": 100},
        {"fieldname": "avg_duration_ms", "label": _("Avg Duration (ms)"), "fieldtype": "Float", "width": 140},
    ]

    rows = frappe.get_all(
        "Integration Log",
        filters=log_filters,
        fields=[
            "integration_name",
            "direction",
            "status",
            "duration_ms",
        ],
        limit_page_length=0,
    )

    buckets = {}
    for row in rows:
        key = (row.integration_name or _("Unspecified"), row.direction or _("Unspecified"))
        bucket = buckets.setdefault(
            key,
            {"request_count": 0, "failed_count": 0, "duration_total": 0},
        )
        bucket["request_count"] += 1
        bucket["failed_count"] += int(row.status == "Failed")
        bucket["duration_total"] += row.duration_ms or 0

    data = []
    for (integration_name, direction), values in sorted(buckets.items()):
        data.append(
            {
                "integration_name": integration_name,
                "direction": direction,
                "status": "Failed" if values["failed_count"] else "Healthy",
                "request_count": values["request_count"],
                "failed_count": values["failed_count"],
                "avg_duration_ms": (
                    values["duration_total"] / values["request_count"]
                    if values["request_count"]
                    else 0
                ),
            }
        )

    return columns, data
