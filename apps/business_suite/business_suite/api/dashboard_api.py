"""Dashboard metrics API for Business Suite.

The endpoint returns permission-aware operational aggregates used by the
Business Suite dashboard. Expensive inventory work is executed as one grouped
query instead of performing one Bin query per product, and the complete result
is cached briefly per authenticated user.
"""

from __future__ import annotations

from datetime import date

import frappe
from frappe import _

from business_suite.api.common import ensure_permission, success
from business_suite.performance import get_dashboard_cache, set_dashboard_cache


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


def _get_low_stock() -> list[dict]:
    """Return the ten most urgent low-stock products with one aggregate query."""
    ensure_permission("Business Product")
    rows = frappe.db.sql(
        """
        SELECT
            bp.name AS product,
            bp.item_code,
            bp.preferred_warehouse AS warehouse,
            COALESCE(SUM(b.actual_qty), 0) AS actual_qty,
            COALESCE(SUM(b.projected_qty), 0) AS projected_qty,
            COALESCE(bp.reorder_level, 0) AS reorder_level
        FROM `tabBusiness Product` bp
        LEFT JOIN `tabBin` b
            ON b.item_code = bp.item_code
           AND (
                COALESCE(bp.preferred_warehouse, '') = ''
                OR b.warehouse = bp.preferred_warehouse
           )
        WHERE bp.active = 1
        GROUP BY
            bp.name,
            bp.item_code,
            bp.preferred_warehouse,
            bp.reorder_level
        HAVING COALESCE(SUM(b.actual_qty), 0) < COALESCE(bp.reorder_level, 0)
        ORDER BY
            (COALESCE(SUM(b.actual_qty), 0) - COALESCE(bp.reorder_level, 0)),
            bp.item_code
        LIMIT 10
        """,
        as_dict=True,
    )
    return [
        {
            "product": row.product,
            "item_code": row.item_code,
            "warehouse": row.warehouse,
            "actual_qty": row.actual_qty or 0,
            "projected_qty": row.projected_qty or 0,
            "reorder_level": row.reorder_level or 0,
        }
        for row in rows
    ]


@frappe.whitelist()
def get_dashboard_summary():
    """Return the operational metrics required by the main dashboard."""
    ensure_permission("Business Customer")
    cached = get_dashboard_cache()
    if cached is not None:
        return cached

    customer_status = _group_count("Business Customer", "onboarding_status")
    request_status = _group_count("Stock Request", "status")
    integration_status = _group_count("Integration Log", "status")

    ensure_permission("Integration Log")
    integration_count = frappe.db.count("Integration Log")

    ensure_permission("Stock Request")
    request_count = frappe.db.count("Stock Request")

    ensure_permission("Business Customer")
    customer_count = frappe.db.count("Business Customer")

    ensure_permission("Business Product")
    product_count = frappe.db.count("Business Product", {"active": 1})
    low_stock = _get_low_stock()

    response = success(
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
            "low_stock": low_stock,
        }
    )
    set_dashboard_cache(response)
    return response
