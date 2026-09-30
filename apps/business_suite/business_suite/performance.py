"""Performance primitives for the Business Suite application.

The performance layer is deliberately small and deployment-safe: indexes are
created idempotently during migration, while dashboard caching is short-lived
and scoped to the authenticated user so permission-aware responses are never
shared across users.
"""

from __future__ import annotations

import frappe

CACHE_TTL_SECONDS = 30
CACHE_PREFIX = "business_suite:dashboard:v1"

# These indexes target the application's repeated filter/group/join paths.
# They are additive and safe to create repeatedly because existence is checked
# against information_schema before issuing DDL.
INDEXES: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    (
        "tabBusiness Customer",
        "idx_bs_customer_onboarding_status",
        ("onboarding_status",),
    ),
    (
        "tabBusiness Product",
        "idx_bs_product_active",
        ("active",),
    ),
    (
        "tabBusiness Product",
        "idx_bs_product_item_warehouse",
        ("item_code", "preferred_warehouse"),
    ),
    (
        "tabStock Request",
        "idx_bs_stock_request_status",
        ("status",),
    ),
    (
        "tabIntegration Log",
        "idx_bs_integration_log_status",
        ("status",),
    ),
    (
        "tabIntegration Log",
        "idx_bs_integration_log_request_id",
        ("request_id",),
    ),
)


def ensure_indexes() -> None:
    """Create application indexes when their DocType tables are available."""
    for table_name, index_name, fields in INDEXES:
        table_exists = frappe.db.sql(
            """
            SELECT 1
            FROM information_schema.tables
            WHERE table_schema = DATABASE() AND table_name = %(table)s
            LIMIT 1
            """,
            {"table": table_name},
        )
        if not table_exists:
            continue

        index_exists = frappe.db.sql(
            """
            SELECT 1
            FROM information_schema.statistics
            WHERE table_schema = DATABASE()
              AND table_name = %(table)s
              AND index_name = %(index)s
            LIMIT 1
            """,
            {"table": table_name, "index": index_name},
        )
        if index_exists:
            continue

        quoted_table = f"`{table_name.replace('`', '``')}`"
        quoted_fields = ", ".join(
            f"`{field.replace('`', '``')}`" for field in fields
        )
        quoted_index = f"`{index_name.replace('`', '``')}`"
        frappe.db.sql(
            f"CREATE INDEX {quoted_index} ON {quoted_table} ({quoted_fields})"
        )


def dashboard_cache_key() -> str:
    """Return a site-local cache key scoped to the current authenticated user."""
    user = frappe.session.user or "Guest"
    return f"{CACHE_PREFIX}:{user}"


def get_dashboard_cache():
    """Return a cached dashboard payload, if one exists."""
    return frappe.cache().get_value(dashboard_cache_key())


def set_dashboard_cache(payload: dict) -> None:
    """Cache a permission-aware dashboard payload for a short interval."""
    frappe.cache().set_value(
        dashboard_cache_key(),
        payload,
        expires_in_sec=CACHE_TTL_SECONDS,
    )
