"""Integration API methods for Business Suite."""

from __future__ import annotations

import frappe
from frappe import _

from business_suite.api.common import ensure_permission, set_response_correlation_id, success
from business_suite.integrations.services.integration_service import IntegrationService


@frappe.whitelist()
def list_logs(limit_start=0, limit_page_length=20, status=None, integration_name=None):
    """Return integration logs with standard Frappe permission filtering."""
    ensure_permission("Integration Log")
    filters = {}
    if status:
        filters["status"] = status
    if integration_name:
        filters["integration_name"] = integration_name
    limit_start = max(int(limit_start or 0), 0)
    limit_page_length = min(max(int(limit_page_length or 20), 1), 100)
    rows = frappe.get_list(
        "Integration Log",
        filters=filters,
        fields=[
            "name", "integration_name", "direction", "endpoint", "request_id",
            "stock_request", "status", "http_status", "error_code",
            "duration_ms", "processed_at", "modified",
        ],
        order_by="modified desc",
        start=limit_start,
        page_length=limit_page_length,
    )
    return success(
        rows,
        limit_start=limit_start,
        limit_page_length=limit_page_length,
        count=len(rows),
    )


@frappe.whitelist()
def get_log(name):
    """Return one integration log with explicit document-level authorization."""
    ensure_permission("Integration Log")
    if not name:
        frappe.throw(_("Integration Log name is required."))
    doc = frappe.get_doc("Integration Log", name)
    return success(doc.as_dict())


@frappe.whitelist()
def enqueue_sync(integration_name, record_id=None):
    """Queue an outbound integration operation and persist an audit record."""
    ensure_permission("Integration Log", "create")
    set_response_correlation_id()
    if not integration_name:
        frappe.throw(_("Integration Name is required."))
    request_id = IntegrationService().enqueue(integration_name, record_id)
    return success(request_id=request_id, status="queued")


@frappe.whitelist()
def retry_log(name):
    """Retry a failed outbound integration using the same request contract."""
    ensure_permission("Integration Log", "write")
    if not name:
        frappe.throw(_("Integration Log name is required."))

    log = frappe.get_doc("Integration Log", name)
    if log.status != "Failed":
        frappe.throw(_("Only failed integrations can be retried."))

    request_id = IntegrationService().retry(log.name)
    return success(request_id=request_id, status="queued")
