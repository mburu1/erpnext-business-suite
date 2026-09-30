app_name = "business_suite"
app_title = "Business Suite"
app_publisher = "Mwangi Wa Mburu"
app_description = "ERPNext business-suite extensions and domain workflows."
app_email = ""
app_license = "MIT"

# RBAC is synchronized on installation and migration so role and DocPerm
# definitions remain reproducible across environments.
after_install = "business_suite.permissions.sync_rbac"
after_migrate = "business_suite.permissions.sync_rbac"

# Row-level authorization hooks. Standard Frappe DocType permissions are
# evaluated first; these hooks add application-specific ownership rules.
has_permission = {
    "Stock Request": "business_suite.permissions.has_permission",
}

permission_query_conditions = {
    "Stock Request": "business_suite.permissions.permission_query_conditions",
}
