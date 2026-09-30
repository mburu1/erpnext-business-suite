"""Shared API authorization, correlation and response helpers."""

from __future__ import annotations

import uuid

import frappe
from frappe import _


def get_correlation_id() -> str:
    """Return the caller correlation ID, creating one when absent."""
    request = getattr(frappe.local, "request", None)
    incoming = request.headers.get("X-Correlation-Id") if request else None
    value = (incoming or "").strip()
    if len(value) > 100:
        value = value[:100]
    correlation_id = value or str(uuid.uuid4())
    frappe.local.business_suite_correlation_id = correlation_id
    return correlation_id


def set_response_correlation_id() -> str:
    """Expose the correlation ID as a response header when HTTP context exists."""
    correlation_id = get_correlation_id()
    response = getattr(frappe.local, "response", None)
    if response is not None:
        response["X-Correlation-Id"] = correlation_id
    return correlation_id


def set_http_status(status_code: int) -> None:
    """Set an HTTP status code without assuming a specific Frappe response object."""
    response = getattr(frappe.local, "response", None)
    if response is not None:
        response.http_status_code = status_code


def ensure_authenticated() -> None:
    set_response_correlation_id()
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
    response["correlation_id"] = getattr(
        frappe.local, "business_suite_correlation_id", get_correlation_id()
    )
    response.update(meta)
    return response
