"""Security hardening helpers for Business Suite.

The app relies on Frappe for authentication and authorization. This module adds
application-level controls that are safe to apply across environments without
embedding secrets or deployment-specific values in source control.
"""

from __future__ import annotations

import re
from collections.abc import Mapping

import frappe
from frappe import _

SAFE_INTEGRATION_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,79}$")
SAFE_HANDLER_PATH = re.compile(r"^business_suite\.integrations\.[A-Za-z0-9_.]+$")
MAX_WEBHOOK_BODY_BYTES = 1_048_576
MAX_EVENT_ID_LENGTH = 140


def validate_integration_name(value: str) -> str:
    """Validate a configuration lookup key before it reaches integration code."""
    name = str(value or "").strip()
    if not SAFE_INTEGRATION_NAME.fullmatch(name):
        frappe.throw(_("Invalid integration name."), frappe.ValidationError)
    return name


def validate_handler_path(value: str | None) -> str | None:
    """Permit only application-owned integration handlers from site configuration."""
    if not value:
        return None
    path = str(value).strip()
    if not SAFE_HANDLER_PATH.fullmatch(path) or "__" in path:
        frappe.throw(_("Invalid integration handler configuration."), frappe.ValidationError)
    return path


def validate_webhook_body_size(raw_body: str | bytes) -> None:
    """Reject oversized webhook bodies before JSON parsing or queueing."""
    size = len(raw_body.encode("utf-8")) if isinstance(raw_body, str) else len(raw_body)
    if size > MAX_WEBHOOK_BODY_BYTES:
        frappe.throw(_("Webhook payload exceeds the maximum allowed size."), frappe.ValidationError)


def validate_event_id(value: str) -> str:
    """Normalize and bound an idempotency/event identifier."""
    event_id = str(value or "").strip()
    if not event_id or len(event_id) > MAX_EVENT_ID_LENGTH:
        frappe.throw(_("Invalid webhook event ID."), frappe.ValidationError)
    return event_id


def apply_security_headers(response):
    """Apply conservative browser security headers without breaking Frappe Desk."""
    headers = response.headers
    headers.setdefault("X-Content-Type-Options", "nosniff")
    headers.setdefault("X-Frame-Options", "SAMEORIGIN")
    headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")

    request = getattr(frappe.local, "request", None)
    if request is not None and request.is_secure:
        headers.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
    return response


def redact_sensitive(value, *, key: str = ""):
    """Return a logging-safe representation of common secret-bearing values."""
    sensitive_markers = (
        "password",
        "secret",
        "token",
        "authorization",
        "api_key",
        "private_key",
        "signature",
    )
    normalized_key = key.lower().replace("-", "_")
    if any(marker in normalized_key for marker in sensitive_markers):
        return "[REDACTED]"
    if isinstance(value, Mapping):
        return {str(k): redact_sensitive(v, key=str(k)) for k, v in value.items()}
    if isinstance(value, list):
        return [redact_sensitive(item) for item in value]
    return value
