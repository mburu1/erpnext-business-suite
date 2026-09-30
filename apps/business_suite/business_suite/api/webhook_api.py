"""Authenticated-by-signature inbound webhook API."""

from __future__ import annotations

import json

import frappe
from frappe import _

from business_suite.api.common import set_http_status, success
from business_suite.integrations.webhooks.handler import handle_event


@frappe.whitelist(allow_guest=True, methods=["POST"])
def receive(integration_name=None):
    """Receive, authenticate, de-duplicate and queue an external webhook."""
    if not integration_name:
        set_http_status(400)
        frappe.throw(_("Integration Name is required."), frappe.ValidationError)

    request = getattr(frappe.local, "request", None)
    if request is None:
        set_http_status(400)
        frappe.throw(_("Webhook requests require an HTTP context."), frappe.ValidationError)

    raw_body = request.get_data(cache=True, as_text=True) or "{}"
    try:
        payload = json.loads(raw_body)
    except json.JSONDecodeError:
        set_http_status(400)
        frappe.throw(_("Webhook payload must be valid JSON."), frappe.ValidationError)

    if not isinstance(payload, dict):
        set_http_status(400)
        frappe.throw(_("Webhook payload must be a JSON object."), frappe.ValidationError)

    event_id = (
        request.headers.get("X-Event-Id")
        or request.headers.get("Idempotency-Key")
        or payload.get("event_id")
    )
    signature = request.headers.get("X-Business-Suite-Signature")
    result = handle_event(
        integration_name,
        payload,
        event_id=event_id,
        raw_body=raw_body,
        signature=signature,
    )
    return success(result)


@frappe.whitelist(allow_guest=True, methods=["GET"])
def health(integration_name=None):
    """Return a minimal provider-facing webhook health response."""
    if not integration_name:
        set_http_status(400)
        frappe.throw(_("Integration Name is required."), frappe.ValidationError)
    return success(integration=integration_name, status="ready")
