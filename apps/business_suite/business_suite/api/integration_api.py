"""Integration API methods for Business Suite."""

import frappe
from frappe import _

from business_suite.api.common import ensure_permission, success
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
        fields=["name", "integration_name", "direction", "request_id", "stock_request", "status",
                "http_status", "error_code", "duration_ms", "processed_at", "modified"],
        order_by="modified desc",
        start=limit_start,
        page_length=limit_page_length,
    )
    return success(rows, limit_start=limit_start, limit_page_length=limit_page_length, count=len(rows))


@frappe.whitelist()
def enqueue_sync(integration_name, record_id=None):
    """Queue an integration operation and persist an audit record."""
    ensure_permission("Integration Log", "create")
    if not integration_name:
        frappe.throw(_("Integration Name is required."))
    request_id = IntegrationService().enqueue(integration_name, record_id)
    return success(request_id=request_id, status="queued")
