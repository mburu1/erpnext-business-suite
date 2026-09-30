"""Inventory API methods for Business Suite."""

import frappe

from business_suite.api.common import ensure_permission, success


@frappe.whitelist()
def list_business_products(limit_start=0, limit_page_length=20, active=None):
    """Return paginated Business Product records."""
    ensure_permission("Business Product")
    filters = {}
    if active not in (None, ""):
        filters["active"] = int(active)
    limit_start = max(int(limit_start or 0), 0)
    limit_page_length = min(max(int(limit_page_length or 20), 1), 100)
    rows = frappe.get_list(
        "Business Product",
        filters=filters,
        fields=["name", "item_code", "category", "reorder_level", "preferred_warehouse", "active", "modified"],
        order_by="modified desc",
        start=limit_start,
        page_length=limit_page_length,
    )
    return success(rows, limit_start=limit_start, limit_page_length=limit_page_length, count=len(rows))


@frappe.whitelist()
def get_stock_snapshot(item_code=None, warehouse=None):
    """Return current ERPNext stock quantities for an optional item/warehouse."""
    ensure_permission("Business Product")
    conditions = ["item_code = %(item_code)s"] if item_code else []
    values = {"item_code": item_code} if item_code else {}
    if warehouse:
        conditions.append("warehouse = %(warehouse)s")
        values["warehouse"] = warehouse
    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    rows = frappe.db.sql(
        f"""
        SELECT item_code, warehouse,
               SUM(actual_qty) AS actual_qty,
               SUM(reserved_qty) AS reserved_qty,
               SUM(projected_qty) AS projected_qty
        FROM tabBin
        {where_clause}
        GROUP BY item_code, warehouse
        ORDER BY item_code, warehouse
        """,
        values,
        as_dict=True,
    )
    return success(rows, count=len(rows))
