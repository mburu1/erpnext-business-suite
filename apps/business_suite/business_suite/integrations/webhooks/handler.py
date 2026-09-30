"""Generic inbound webhook processing helpers."""

from __future__ import annotations

import uuid

import frappe


def handle_event(integration_name: str, payload: dict, *, event_id: str | None = None) -> dict:
    """Persist a webhook receipt and make duplicate delivery idempotent."""
    event_id = event_id or str(uuid.uuid4())
    existing = frappe.db.exists("Integration Log", {"request_id": event_id, "direction": "Inbound"})
    if existing:
        return {"success": True, "duplicate": True, "request_id": event_id}

    log = frappe.get_doc(
        {
            "doctype": "Integration Log",
            "integration_name": integration_name,
            "direction": "Inbound",
            "request_id": event_id,
            "status": "Completed",
            "processed_at": frappe.utils.now_datetime(),
        }
    )
    log.insert(ignore_permissions=True)
    return {"success": True, "duplicate": False, "request_id": event_id}
