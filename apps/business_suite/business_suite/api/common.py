"""Shared API helpers for Business Suite endpoints."""

import frappe
from frappe import _


def ensure_authenticated():
    if frappe.session.user == "Guest":
        frappe.throw(_("Authentication is required."), frappe.PermissionError)


def ensure_permission(doctype, ptype="read"):
    ensure_authenticated()
    if not frappe.has_permission(doctype=doctype, ptype=ptype):
        frappe.throw(
            _("You do not have permission to {0} {1}.").format(ptype, doctype),
            frappe.PermissionError,
        )


def success(data=None, **meta):
    response = {"success": True}
    if data is not None:
        response["data"] = data
    response.update(meta)
    return response
