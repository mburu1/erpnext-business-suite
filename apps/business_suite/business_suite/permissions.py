"""Business Suite role-based access control (RBAC)."""

from __future__ import annotations

import frappe
from frappe import _

ROLE_ADMIN = "Business Suite Administrator"
ROLE_MANAGER = "Business Suite Manager"
ROLE_SALES = "Business Suite Sales User"
ROLE_INVENTORY = "Business Suite Inventory User"
ROLE_INTEGRATION = "Business Suite Integration User"
ROLE_REPORT = "Business Suite Report User"

ROLES = (
    ROLE_ADMIN, ROLE_MANAGER, ROLE_SALES,
    ROLE_INVENTORY, ROLE_INTEGRATION, ROLE_REPORT,
)

DOCTYPE_PERMISSIONS = {
    "Business Customer": {
        ROLE_ADMIN: {"read": 1, "write": 1, "create": 1, "delete": 1, "report": 1, "export": 1, "print": 1, "email": 1},
        ROLE_MANAGER: {"read": 1, "write": 1, "create": 1, "delete": 1, "report": 1, "export": 1, "print": 1, "email": 1},
        ROLE_SALES: {"read": 1, "write": 1, "create": 1, "report": 1, "export": 1, "print": 1, "email": 1},
        ROLE_REPORT: {"read": 1, "report": 1, "export": 1, "print": 1},
    },
    "Business Product": {
        ROLE_ADMIN: {"read": 1, "write": 1, "create": 1, "delete": 1, "report": 1, "export": 1, "print": 1},
        ROLE_MANAGER: {"read": 1, "write": 1, "create": 1, "delete": 1, "report": 1, "export": 1, "print": 1},
        ROLE_INVENTORY: {"read": 1, "write": 1, "create": 1, "delete": 1, "report": 1, "export": 1, "print": 1},
        ROLE_SALES: {"read": 1, "report": 1, "export": 1, "print": 1},
        ROLE_REPORT: {"read": 1, "report": 1, "export": 1, "print": 1},
    },
    "Stock Request": {
        ROLE_ADMIN: {"read": 1, "write": 1, "create": 1, "delete": 1, "report": 1, "export": 1, "print": 1},
        ROLE_MANAGER: {"read": 1, "write": 1, "create": 1, "delete": 1, "report": 1, "export": 1, "print": 1},
        ROLE_INVENTORY: {"read": 1, "write": 1, "create": 1, "report": 1, "export": 1, "print": 1},
        ROLE_SALES: {"read": 1, "write": 1, "create": 1, "report": 1, "print": 1},
        ROLE_REPORT: {"read": 1, "report": 1, "export": 1, "print": 1},
    },
    "Integration Log": {
        ROLE_ADMIN: {"read": 1, "write": 1, "create": 1, "delete": 1, "report": 1, "export": 1, "print": 1},
        ROLE_MANAGER: {"read": 1, "report": 1, "export": 1, "print": 1},
        ROLE_INTEGRATION: {"read": 1, "write": 1, "create": 1, "report": 1, "export": 1, "print": 1},
        ROLE_REPORT: {"read": 1, "report": 1, "export": 1, "print": 1},
    },
}

def _has_role(user: str, role: str) -> bool:
    return bool(user and role in frappe.get_roles(user))

def _ensure_role(role_name: str) -> None:
    if not frappe.db.exists("Role", role_name):
        frappe.get_doc({
            "doctype": "Role",
            "role_name": role_name,
            "desk_access": 1,
            "is_custom": 1,
        }).insert(ignore_permissions=True)

def _permission_exists(doctype: str, role: str) -> bool:
    return bool(frappe.db.exists(
        "DocPerm", {"parent": doctype, "role": role, "permlevel": 0}
    ))

def _upsert_permission(doctype: str, role: str, values: dict) -> None:
    if _permission_exists(doctype, role):
        frappe.db.set_value(
            "DocPerm",
            {"parent": doctype, "role": role, "permlevel": 0},
            values,
            update_modified=False,
        )
        return
    frappe.get_doc({
        "doctype": "DocPerm",
        "parent": doctype,
        "parenttype": "DocType",
        "parentfield": "permissions",
        "role": role,
        "permlevel": 0,
        **values,
    }).insert(ignore_permissions=True)

def sync_rbac() -> None:
    """Create/update Business Suite roles and their DocType permissions."""
    for role in ROLES:
        _ensure_role(role)
    for doctype, role_map in DOCTYPE_PERMISSIONS.items():
        if not frappe.db.exists("DocType", doctype):
            continue
        for role, values in role_map.items():
            _upsert_permission(doctype, role, values)
    frappe.clear_cache()

def has_permission(doc, user=None, permission_type=None):
    """Apply record-level restrictions after normal RBAC is evaluated."""
    user = user or frappe.session.user
    permission_type = permission_type or "read"
    if user == "Administrator" or _has_role(user, ROLE_ADMIN):
        return True
    if doc.doctype == "Stock Request":
        if _has_role(user, ROLE_MANAGER) or _has_role(user, ROLE_INVENTORY):
            return True
        if permission_type in {"read", "write", "create"}:
            return doc.get("requested_by") == user
    return None

def permission_query_conditions(user=None):
    """Return SQL conditions for user-owned Stock Request records."""
    user = user or frappe.session.user
    if user == "Administrator" or _has_role(user, ROLE_ADMIN):
        return ""
    if _has_role(user, ROLE_MANAGER) or _has_role(user, ROLE_INVENTORY):
        return ""
    return "requested_by = " + frappe.db.escape(user)

def validate_role(role: str) -> None:
    """Raise PermissionError when the current user lacks an application role."""
    if frappe.session.user == "Administrator":
        return
    if role not in frappe.get_roles(frappe.session.user):
        frappe.throw(
            _("The current user requires the {0} role.").format(role),
            frappe.PermissionError,
        )
