"""Shared API authorization and response helpers."""

import frappe
from frappe import _


def ensure_authenticated() -> None:
    if frappe.session.user == "Guest":
        frappe.throw(_("Authentication is required."), frappe.PermissionError)


def ensure_permission(doctype: str, ptype: str = "read") -> None:
    ensure_authenticated()
    if not frappe.has_permission(doctype=doctype, ptype=ptype):
        frappe.throw(
            _("You do not have permission to {0} {1}.").format(ptype, doctype),
            frappe.PermissionError,
        )


def ensure_document_permission(doc, ptype: str = "read") -> None:
    from business_suite.permissions import ensure_document_permission as _check

    _check(doc, ptype)


def ensure_allowed_doctype(doctype: str, allowed: set[str]) -> None:
    ensure_authenticated()
    if doctype not in allowed:
        frappe.throw(_("Unsupported Business Suite DocType."), frappe.PermissionError)


def parse_payload(data) -> dict:
    payload = frappe.parse_json(data) if isinstance(data, str) else data
    if not isinstance(payload, dict):
        frappe.throw(_("Request data must be a JSON object."), frappe.ValidationError)
    return payload


def success(data=None, **meta):
    response = {"success": True}
    if data is not None:
        response["data"] = data
    response.update(meta)
    return response
