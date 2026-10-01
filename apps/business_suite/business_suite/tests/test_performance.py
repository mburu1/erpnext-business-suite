"""Performance and scalability regression contracts."""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
APP_ROOT = REPO_ROOT / "apps" / "business_suite" / "business_suite"


def test_performance_layer_defines_idempotent_indexes_and_short_cache():
    source = (APP_ROOT / "performance.py").read_text(encoding="utf-8")
    assert "information_schema.statistics" in source
    assert "CREATE INDEX" in source
    assert "expires_in_sec=CACHE_TTL_SECONDS" in source
    assert "business_suite:dashboard:v1" in source


def test_dashboard_uses_set_based_low_stock_query_and_cache():
    source = (APP_ROOT / "api" / "dashboard_api.py").read_text(encoding="utf-8")
    assert "get_dashboard_cache()" in source
    assert "set_dashboard_cache(response)" in source
    assert "LEFT JOIN `tabBin`" in source
    assert "LIMIT 10" in source
    assert "frappe.get_all(\n            \"Bin\"" not in source


def test_inventory_snapshot_is_bounded():
    source = (APP_ROOT / "api" / "inventory_api.py").read_text(encoding="utf-8")
    assert "limit_page_length = min(max(int(limit_page_length or 100), 1), 500)" in source
    assert "LIMIT %(limit_start)s, %(limit_page_length)s" in source


def test_performance_indexes_are_registered_for_migrations():
    hooks = (APP_ROOT / "hooks.py").read_text(encoding="utf-8")
    assert "business_suite.performance.ensure_indexes" in hooks
    assert "after_migrate = [" in hooks
