"""Inbound webhook authentication, idempotency and queueing."""

from __future__ import annotations

import hashlib
import hmac
import uuid

import frappe
from frappe import _

from business_suite.security import (
    validate_event_id,
    validate_handler_path,
    validate_integration_name,
    validate_webhook_body_size,
)


def _webhook_config(integration_name: str) -> dict:
    integration_name = validate_integration_name(integration_name)
    config = frappe.conf.get("business_suite_integrations") or {}
    if not isinstance(config, dict):
        return {}
    webhooks = config.get("webhooks") or {}
    value = webhooks.get(integration_name)
    return value if isinstance(value, dict) else {}


def verify_signature(
    integration_name: str,
    raw_body: str,
    signature: str | None,
) -> bool:
    """Verify an HMAC-SHA256 webhook signature from site configuration."""
    validate_webhook_body_size(raw_body)
    config = _webhook_config(integration_name)
    secret = config.get("secret")
    if not secret:
        return False

    expected = hmac.new(
        str(secret).encode("utf-8"),
        raw_body.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    supplied = (signature or "").strip()
    if supplied.startswith("sha256="):
        supplied = supplied[7:]
    return bool(supplied) and hmac.compare_digest(supplied, expected)


def handle_event(
    integration_name: str,
    payload: dict,
    *,
    event_id: str | None = None,
    raw_body: str | None = None,
    signature: str | None = None,
) -> dict:
    """Authenticate, persist and queue a webhook exactly once."""
    integration_name = validate_integration_name(integration_name)
    if not isinstance(payload, dict):
        frappe.throw(_("Webhook payload must be a JSON object."), frappe.ValidationError)

    if raw_body is not None:
        validate_webhook_body_size(raw_body)

    config = _webhook_config(integration_name)
    if not config:
        frappe.throw(
            _("Webhook integration {0} is not configured.").format(integration_name),
            frappe.ValidationError,
        )

    if config.get("require_signature", True):
        if raw_body is None or not verify_signature(integration_name, raw_body, signature):
            frappe.throw(_("Invalid webhook signature."), frappe.AuthenticationError)

    event_id = validate_event_id(event_id or payload.get("event_id") or str(uuid.uuid4()))

    existing = frappe.db.exists(
        "Integration Log",
        {"request_id": event_id, "direction": "Inbound"},
    )
    if existing:
        return {"success": True, "duplicate": True, "request_id": event_id}

    log = frappe.get_doc(
        {
            "doctype": "Integration Log",
            "integration_name": integration_name,
            "direction": "Inbound",
            "endpoint": "/api/method/business_suite.api.webhook_api.receive",
            "request_id": event_id,
            "status": "Queued",
        }
    )
    log.flags.internal_integration = True
    log.insert(ignore_permissions=True)

    frappe.enqueue(
        "business_suite.integrations.webhooks.handler.process_webhook",
        queue="short",
        integration_log=log.name,
        payload=payload,
        enqueue_after_commit=True,
    )

    return {
        "success": True,
        "duplicate": False,
        "request_id": event_id,
        "status": "queued",
    }


def process_webhook(integration_log: str, payload: dict) -> None:
    """Process a webhook asynchronously and persist its terminal state."""
    log = frappe.get_doc("Integration Log", integration_log)
    log.flags.internal_integration = True
    started = frappe.utils.now_datetime()
    try:
        log.status = "Processing"
        log.save(ignore_permissions=True)

        config = _webhook_config(log.integration_name)
        method_path = validate_handler_path(config.get("handler"))
        if method_path:
            frappe.get_attr(method_path)(payload)

        log.status = "Completed"
        log.processed_at = frappe.utils.now_datetime()
        log.duration_ms = int(
            (frappe.utils.now_datetime() - started).total_seconds() * 1000
        )
        log.save(ignore_permissions=True)
    except Exception:
        frappe.log_error(
            frappe.get_traceback(),
            _("Business Suite webhook processing failed"),
        )
        log.status = "Failed"
        log.error_code = "WEBHOOK_PROCESSING_ERROR"
        log.processed_at = frappe.utils.now_datetime()
        log.duration_ms = int(
            (frappe.utils.now_datetime() - started).total_seconds() * 1000
        )
        log.save(ignore_permissions=True)
