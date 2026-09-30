"""Authenticated-by-signature inbound webhook API."""

from __future__ import annotations

import json

import frappe
from frappe import _
from frappe.rate_limiter import rate_limit

from business_suite.api.common import set_http_status, success
from business_suite.integrations.webhooks.handler import handle_event
from business_suite.security import validate_event_id, validate_integration_name, validate_webhook_body_size


@frappe.whitelist(allow_guest=True, methods=["POST"])
@rate_limit(limit=30, seconds=60, ip_based=True, methods="POST")
def receive(integration_name=None):
    """Receive, authenticate, de-duplicate and queue an external webhook."""
    try:
        integration_name = validate_integration_name(integration_name)
    except Exception:
        set_http_status(400)
        raise

    request = getattr(frappe.local, "request", None)
    if request is None:
        set_http_status(400)
        frappe.throw(_("Webhook requests require an HTTP context."), frappe.ValidationError)

    raw_body = request.get_data(cache=True, as_text=True) or "{}"
    validate_webhook_body_size(raw_body)
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
    if event_id:
        event_id = validate_event_id(event_id)
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
@rate_limit(limit=60, seconds=60, ip_based=True, methods="GET")
def health(integration_name=None):
    """Return a minimal provider-facing webhook health response."""
    integration_name = validate_integration_name(integration_name)
    return success(integration=integration_name, status="ready")
