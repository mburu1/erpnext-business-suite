"""Inventory Summary script report."""

import frappe
from frappe import _


def execute(filters=None):
    filters = filters or {}
    product_filters = {}
    if filters.get("active") not in (None, ""):
        product_filters["active"] = int(filters["active"])
    if filters.get("warehouse"):
        product_filters["preferred_warehouse"] = filters["warehouse"]

    products = frappe.get_all(
        "Business Product",
        filters=product_filters,
        fields=["name", "item_code", "preferred_warehouse", "reorder_level"],
        order_by="item_code",
    )

    columns = [
        {"fieldname": "name", "label": _("Business Product"), "fieldtype": "Link", "options": "Business Product", "width": 160},
        {"fieldname": "item_code", "label": _("Item"), "fieldtype": "Link", "options": "Item", "width": 160},
        {"fieldname": "warehouse", "label": _("Warehouse"), "fieldtype": "Link", "options": "Warehouse", "width": 180},
        {"fieldname": "reorder_level", "label": _("Reorder Level"), "fieldtype": "Float", "width": 110},
        {"fieldname": "actual_qty", "label": _("Actual Qty"), "fieldtype": "Float", "width": 110},
        {"fieldname": "projected_qty", "label": _("Projected Qty"), "fieldtype": "Float", "width": 110},
        {"fieldname": "below_reorder", "label": _("Below Reorder"), "fieldtype": "Check", "width": 110},
    ]

    data = []
    for product in products:
        bin_filters = {"item_code": product.item_code}
        if product.preferred_warehouse:
            bin_filters["warehouse"] = product.preferred_warehouse

        bins = frappe.get_all(
            "Bin",
            filters=bin_filters,
            fields=["actual_qty", "projected_qty"],
        )
        actual_qty = sum((row.actual_qty or 0) for row in bins)
        projected_qty = sum((row.projected_qty or 0) for row in bins)
        reorder_level = product.reorder_level or 0

        data.append(
            {
                "name": product.name,
                "item_code": product.item_code,
                "warehouse": product.preferred_warehouse,
                "reorder_level": reorder_level,
                "actual_qty": actual_qty,
                "projected_qty": projected_qty,
                "below_reorder": int(actual_qty < reorder_level),
            }
        )

    data.sort(key=lambda row: (-row["below_reorder"], row["item_code"] or ""))
    return columns, data
