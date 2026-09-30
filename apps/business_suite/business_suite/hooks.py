app_name = "business_suite"
app_title = "Business Suite"
app_publisher = "Mwangi Wa Mburu"
app_description = "ERPNext business-suite extensions and domain workflows."
app_email = ""
app_license = "MIT"

# RBAC and performance indexes are synchronized during installation and migration.
after_install = [
    "business_suite.permissions.sync_rbac",
    "business_suite.performance.ensure_indexes",
]
after_migrate = [
    "business_suite.permissions.sync_rbac",
    "business_suite.performance.ensure_indexes",
]

# Row-level authorization hooks. Standard Frappe DocType permissions are
evaluated first; these hooks add application-specific ownership rules.
has_permission = {
    "Stock Request": "business_suite.permissions.has_permission",
}

permission_query_conditions = {
    "Stock Request": "business_suite.permissions.permission_query_conditions",
}

# Conservative HTTP hardening that does not require deployment-specific
# configuration or a custom reverse proxy implementation.
after_request = [
    "business_suite.security.apply_security_headers",
    "business_suite.observability.after_request",
]

# Establish request correlation and timing before application handlers run.
before_request = ["business_suite.observability.before_request"]
