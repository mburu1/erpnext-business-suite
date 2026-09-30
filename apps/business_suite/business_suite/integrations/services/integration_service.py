"""Outbound integration orchestration and audit logging."""

from __future__ import annotations

import uuid

import frappe
from frappe import _


class IntegrationService:
    """Create auditable integration jobs without coupling domain code to providers."""

    def _config(self, integration_name: str) -> dict:
        config = frappe.conf.get("business_suite_integrations") or {}
        if not isinstance(config, dict):
            return {}
        value = config.get(integration_name)
        return value if isinstance(value, dict) else {}

    def enqueue(self, integration_name: str, record_id: str | None = None) -> str:
        if not integration_name or len(integration_name) > 100:
            frappe.throw(_("A valid Integration Name is required."))

        config = self._config(integration_name)
        if not config.get("base_url"):
            frappe.throw(
                _("Integration {0} is not configured.").format(integration_name),
                frappe.ValidationError,
            )

        request_id = str(uuid.uuid4())
        log = frappe.get_doc(
            {
                "doctype": "Integration Log",
                "integration_name": integration_name,
                "direction": "Outbound",
                "endpoint": config.get("path", "/"),
                "request_id": request_id,
                "stock_request": (
                    record_id
                    if record_id and frappe.db.exists("Stock Request", record_id)
                    else None
                ),
                "status": "Queued",
            }
        )
        log.flags.internal_integration = True
        log.insert(ignore_permissions=True)
        frappe.enqueue(
            "business_suite.integrations.services.integration_service.process_integration",
            queue="short",
            integration_log=log.name,
            enqueue_after_commit=True,
        )
        return request_id

    def retry(self, integration_log: str) -> str:
        log = frappe.get_doc("Integration Log", integration_log)
        if log.status != "Failed":
            frappe.throw(_("Only failed integrations can be retried."))

        request_id = str(uuid.uuid4())
        log.request_id = request_id
        log.status = "Queued"
        log.error_code = None
        log.http_status = None
        log.duration_ms = None
        log.processed_at = None
        log.flags.internal_integration = True
        log.save(ignore_permissions=True)

        frappe.enqueue(
            "business_suite.integrations.services.integration_service.process_integration",
            queue="short",
            integration_log=log.name,
            enqueue_after_commit=True,
        )
        return request_id


def _build_payload(log, config: dict) -> dict:
    """Build an outbound JSON object from configured static data and linked records."""
    payload = config.get("payload")
    result = dict(payload) if isinstance(payload, dict) else {}

    if log.stock_request:
        result["stock_request"] = frappe.get_doc("Stock Request", log.stock_request).as_dict()

    result.setdefault("request_id", log.request_id)
    result.setdefault("integration_name", log.integration_name)
    return result


def process_integration(integration_log: str) -> None:
    """Process a queued integration using site configuration."""
    from business_suite.integrations.clients.rest_client import RestClient

    log = frappe.get_doc("Integration Log", integration_log)
    log.flags.internal_integration = True
    started = frappe.utils.now_datetime()
    config = IntegrationService()._config(log.integration_name)

    log.status = "Processing"
    log.save(ignore_permissions=True)

    if not config.get("base_url"):
        _fail(log, "INTEGRATION_NOT_CONFIGURED", started)
        return

    try:
        path = str(config.get("path", "/health"))
        if "{record_id}" in path:
            path = path.format(record_id=log.stock_request or "")

        headers = dict(config.get("headers") or {})
        headers.setdefault("X-Correlation-Id", log.request_id)
        headers.setdefault("X-Idempotency-Key", log.request_id)

        client = RestClient(
            config["base_url"],
            timeout=(
                float(config.get("connect_timeout", 5)),
                float(config.get("read_timeout", 30)),
            ),
            max_retries=int(config.get("max_retries", 2)),
            backoff_seconds=float(config.get("backoff_seconds", 0.5)),
        )
        status, _, duration_ms = client.request(
            config.get("method", "POST"),
            path,
            headers=headers,
            json=_build_payload(log, config),
        )
        log.endpoint = path
        log.http_status = status
        log.duration_ms = duration_ms
        log.status = "Completed" if 200 <= status < 300 else "Failed"
        log.error_code = None if log.status == "Completed" else f"HTTP_{status}"
        log.processed_at = frappe.utils.now_datetime()
        log.save(ignore_permissions=True)
    except Exception:
        frappe.log_error(
            frappe.get_traceback(),
            _("Business Suite integration processing failed"),
        )
        _fail(log, "INTEGRATION_TRANSPORT_ERROR", started)


def _fail(log, error_code: str, started) -> None:
    log.flags.internal_integration = True
    log.status = "Failed"
    log.error_code = error_code
    log.processed_at = frappe.utils.now_datetime()
    log.duration_ms = int(
        (frappe.utils.now_datetime() - started).total_seconds() * 1000
    )
    log.save(ignore_permissions=True)
