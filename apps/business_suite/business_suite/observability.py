"""Application observability hooks and health diagnostics.

The implementation deliberately uses Frappe's native logging and request
lifecycle hooks so observability does not add a mandatory third-party runtime
dependency. Metrics are process-local and are intended for diagnostics; the
structured request log is the durable source that can be shipped to a log
aggregator.
"""

from __future__ import annotations

import json
import time
import uuid
from threading import Lock
from typing import Any

import frappe


_SLOW_REQUEST_SECONDS = 1.0
_MAX_PATH_LENGTH = 512
_MAX_USER_LENGTH = 140

_metrics: dict[str, int] = {
    "requests_total": 0,
    "requests_2xx": 0,
    "requests_3xx": 0,
    "requests_4xx": 0,
    "requests_5xx": 0,
    "requests_slow": 0,
}
_metrics_lock = Lock()


def _logger():
    return frappe.logger("business_suite.observability", allow_site=True)


def _increment(metric: str) -> None:
    with _metrics_lock:
        _metrics[metric] = _metrics.get(metric, 0) + 1


def _request_id() -> str:
    request_id = getattr(frappe.local, "business_suite_request_id", None)
    if not request_id:
        request_id = str(uuid.uuid4())
        frappe.local.business_suite_request_id = request_id
    return request_id


def before_request() -> None:
    """Start request timing and establish a correlation ID."""
    frappe.local.business_suite_request_id = str(uuid.uuid4())
    frappe.local.business_suite_request_started_at = time.perf_counter()


def after_request(response: Any) -> Any:
    """Record a structured request event and expose the correlation ID."""
    started_at = getattr(frappe.local, "business_suite_request_started_at", None)
    duration_ms = round((time.perf_counter() - started_at) * 1000, 2) if started_at else None
    status = int(getattr(response, "status_code", 200) or 200)
    request_id = _request_id()

    _increment("requests_total")
    if 200 <= status < 300:
        _increment("requests_2xx")
    elif 300 <= status < 400:
        _increment("requests_3xx")
    elif 400 <= status < 500:
        _increment("requests_4xx")
    else:
        _increment("requests_5xx")

    slow = duration_ms is not None and duration_ms >= (_SLOW_REQUEST_SECONDS * 1000)
    if slow:
        _increment("requests_slow")

    response.headers["X-Request-ID"] = request_id
    if duration_ms is not None:
        response.headers["Server-Timing"] = f"app;dur={duration_ms}"

    request = getattr(frappe.local, "request", None)
    event = {
        "event": "http_request",
        "request_id": request_id,
        "method": getattr(request, "method", None),
        "path": str(getattr(request, "path", ""))[:_MAX_PATH_LENGTH],
        "status_code": status,
        "duration_ms": duration_ms,
        "slow": slow,
        "user": str(getattr(frappe.session, "user", "Guest"))[:_MAX_USER_LENGTH],
    }
    _logger().info(json.dumps(event, separators=(",", ":"), default=str))
    return response


@frappe.whitelist()
def get_observability_status() -> dict[str, Any]:
    """Return a lightweight authenticated application health snapshot."""
    database = "ok"
    try:
        frappe.db.sql("SELECT 1")
    except Exception:
        database = "error"
        _logger().exception("Database health check failed")

    with _metrics_lock:
        metrics = dict(_metrics)

    return {
        "status": "ok" if database == "ok" else "degraded",
        "database": database,
        "site": frappe.local.site,
        "request_id": _request_id(),
        "metrics": metrics,
    }
