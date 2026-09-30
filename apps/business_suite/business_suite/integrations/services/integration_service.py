"""Integration orchestration and audit logging."""

from __future__ import annotations

import uuid

import frappe
from frappe import _


class IntegrationService:
    """Create auditable integration jobs without coupling to a provider."""

    def enqueue(self, integration_name: str, record_id: str | None = None) -> str:
        request_id = str(uuid.uuid4())
        log = frappe.get_doc(
            {
                "doctype": "Integration Log",
                "integration_name": integration_name,
                "direction": "Outbound",
                "request_id": request_id,
                "stock_request": record_id if record_id and frappe.db.exists("Stock Request", record_id) else None,
                "status": "Queued",
            }
        )
        log.insert(ignore_permissions=True)
        frappe.enqueue(
            "business_suite.integrations.services.integration_service.process_integration",
            queue="short",
            integration_log=log.name,
            enqueue_after_commit=True,
        )
        return request_id


def process_integration(integration_log: str) -> None:
    """Process a queued integration using site configuration."""
    from business_suite.integrations.clients.rest_client import RestClient

    log = frappe.get_doc("Integration Log", integration_log)
    started = frappe.utils.now_datetime()
    config = frappe.conf.get("business_suite_integrations") or {}
    integration_config = config.get(log.integration_name) if isinstance(config, dict) else None

    log.status = "Processing"
    log.save(ignore_permissions=True)

    if not integration_config or not integration_config.get("base_url"):
        log.status = "Failed"
        log.error_code = "INTEGRATION_NOT_CONFIGURED"
        log.processed_at = frappe.utils.now_datetime()
        log.duration_ms = int((frappe.utils.now_datetime() - started).total_seconds() * 1000)
        log.save(ignore_permissions=True)
        return

    try:
        client = RestClient(
            integration_config["base_url"],
            timeout=(float(integration_config.get("connect_timeout", 5)), float(integration_config.get("read_timeout", 30))),
        )
        status, _, duration_ms = client.request(
            integration_config.get("method", "GET"),
            integration_config.get("path", "/health"),
            headers=integration_config.get("headers") or {},
        )
        log.http_status = status
        log.duration_ms = duration_ms
        log.status = "Completed" if 200 <= status < 300 else "Failed"
        if log.status == "Failed":
            log.error_code = f"HTTP_{status}"
        log.processed_at = frappe.utils.now_datetime()
        log.save(ignore_permissions=True)
    except Exception:
        frappe.log_error(frappe.get_traceback(), _("Business Suite integration processing failed"))
        log.status = "Failed"
        log.error_code = "INTEGRATION_TRANSPORT_ERROR"
        log.processed_at = frappe.utils.now_datetime()
        log.duration_ms = int((frappe.utils.now_datetime() - started).total_seconds() * 1000)
        log.save(ignore_permissions=True)
