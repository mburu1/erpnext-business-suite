"""Customer-facing API methods for the Business Suite app."""

import frappe
from frappe import _

from business_suite.api.common import ensure_permission, success


@frappe.whitelist()
def list_business_customers(limit_start=0, limit_page_length=20, status=None):
    """Return paginated Business Customer records respecting Frappe permissions."""
    ensure_permission("Business Customer")
    filters = {"onboarding_status": status} if status else {}
    limit_start = max(int(limit_start or 0), 0)
    limit_page_length = min(max(int(limit_page_length or 20), 1), 100)
    rows = frappe.get_list(
        "Business Customer",
        filters=filters,
        fields=["name", "customer", "onboarding_status", "segment", "risk_level", "approved_by", "modified"],
        order_by="modified desc",
        start=limit_start,
        page_length=limit_page_length,
    )
    return success(rows, limit_start=limit_start, limit_page_length=limit_page_length, count=len(rows))


@frappe.whitelist()
def get_business_customer(name):
    """Return one Business Customer after an explicit permission check."""
    ensure_permission("Business Customer")
    if not name:
        frappe.throw(_("Business Customer name is required."))
    return success(frappe.get_doc("Business Customer", name).as_dict())
