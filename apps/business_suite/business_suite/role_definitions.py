"""Framework-independent Business Suite role definitions.

Keeping role identifiers outside the Frappe integration layer makes the
authorization model directly unit-testable without a running site.
"""

ROLE_ADMIN = "Business Suite Administrator"
ROLE_MANAGER = "Business Suite Manager"
ROLE_SALES = "Business Suite Sales User"
ROLE_INVENTORY = "Business Suite Inventory User"
ROLE_INTEGRATION = "Business Suite Integration User"
ROLE_REPORT = "Business Suite Report User"

ROLES = (
    ROLE_ADMIN,
    ROLE_MANAGER,
    ROLE_SALES,
    ROLE_INVENTORY,
    ROLE_INTEGRATION,
    ROLE_REPORT,
)
