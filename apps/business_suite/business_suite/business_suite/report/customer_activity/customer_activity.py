"""Customer Activity script report."""

import frappe
from frappe import _


def execute(filters=None):
    filters = filters or {}
    filters = {key: value for key, value in filters.items() if value}
    columns = [
        {"fieldname": "name", "label": _("Business Customer"), "fieldtype": "Link", "options": "Business Customer", "width": 160},
        {"fieldname": "customer", "label": _("Customer"), "fieldtype": "Link", "options": "Customer", "width": 180},
        {"fieldname": "onboarding_status", "label": _("Onboarding Status"), "fieldtype": "Data", "width": 130},
        {"fieldname": "segment", "label": _("Segment"), "fieldtype": "Data", "width": 130},
        {"fieldname": "risk_level", "label": _("Risk Level"), "fieldtype": "Data", "width": 100},
        {"fieldname": "modified", "label": _("Last Modified"), "fieldtype": "Datetime", "width": 150},
    ]
    data = frappe.get_all(
        "Business Customer",
        filters=filters,
        fields=["name", "customer", "onboarding_status", "segment", "risk_level", "modified"],
        order_by="modified desc",
    )
    return columns, data
