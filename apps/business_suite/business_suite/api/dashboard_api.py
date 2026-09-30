"""Dashboard metrics API for Business Suite.

The endpoint returns permission-aware operational aggregates used by the
Business Suite dashboard. It deliberately returns aggregates rather than
raw records so the dashboard stays lightweight and avoids exposing fields
that are not needed for visualization.
"""

from __future__ import annotations

from datetime import date

import frappe
from frappe import _

from business_suite.api.common import ensure_permission, success


def _group_count(doctype: str, fieldname: str) -> list[dict]:
    """Return permission-aware counts grouped by a DocType field."""
    ensure_permission(doctype)
    rows = frappe.get_all(
        doctype,
        fields=[fieldname, "count(name) as count"],
        group_by=fieldname,
        order_by="count desc",
    )
    return [
        {
            "label": row.get(fieldname) or _("Unspecified"),
            "count": int(row.get("count") or 0),
        }
        for row in rows
    ]


@frappe.whitelist()
def get_dashboard_summary():
    """Return the operational metrics required by the main dashboard."""
    customer_status = _group_count("Business Customer", "onboarding_status")
    request_status = _group_count("Stock Request", "status")
    integration_status = _group_count("Integration Log", "status")

    ensure_permission("Business Product")
    products = frappe.get_all(
        "Business Product",
        fields=["name", "item_code", "reorder_level", "preferred_warehouse"],
        filters={"active": 1},
        order_by="item_code",
        limit_page_length=1000,
    )

    low_stock = []
    for product in products:
        if not product.item_code:
            continue

        filters = {"item_code": product.item_code}
        if product.preferred_warehouse:
            filters["warehouse"] = product.preferred_warehouse

        stock = frappe.get_all(
            "Bin",
            filters=filters,
            fields=["actual_qty", "projected_qty"],
        )
        actual_qty = sum((row.actual_qty or 0) for row in stock)
        projected_qty = sum((row.projected_qty or 0) for row in stock)
        reorder_level = product.reorder_level or 0

        if actual_qty < reorder_level:
            low_stock.append(
                {
                    "product": product.name,
                    "item_code": product.item_code,
                    "warehouse": product.preferred_warehouse,
                    "actual_qty": actual_qty,
                    "projected_qty": projected_qty,
                    "reorder_level": reorder_level,
                }
            )

    low_stock.sort(key=lambda row: (row["actual_qty"] - row["reorder_level"], row["item_code"]))

    ensure_permission("Integration Log")
    integration_count = frappe.db.count("Integration Log")

    ensure_permission("Stock Request")
    request_count = frappe.db.count("Stock Request")

    ensure_permission("Business Customer")
    customer_count = frappe.db.count("Business Customer")

    ensure_permission("Business Product")
    product_count = frappe.db.count("Business Product", {"active": 1})

    return success(
        {
            "as_of": date.today().isoformat(),
            "kpis": {
                "customers": int(customer_count),
                "active_products": int(product_count),
                "stock_requests": int(request_count),
                "integration_logs": int(integration_count),
                "low_stock_items": len(low_stock),
            },
            "customer_status": customer_status,
            "stock_request_status": request_status,
            "integration_status": integration_status,
            "low_stock": low_stock[:10],
        }
    )
