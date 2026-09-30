"""Business Suite role-based access control (RBAC)."""

from __future__ import annotations

import frappe
from frappe import _

from business_suite.role_definitions import (
    ROLE_ADMIN,
    ROLE_INTEGRATION,
    ROLE_INVENTORY,
    ROLE_MANAGER,
    ROLE_REPORT,
    ROLE_SALES,
    ROLES,
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

MANAGED_DOCTYPES = tuple(DOCTYPE_PERMISSIONS)


def has_role(user: str, role: str) -> bool:
    return bool(user and (user == "Administrator" or role in frappe.get_roles(user)))


def has_any_role(user: str, roles: set[str] | tuple[str, ...]) -> bool:
    return bool(user and (user == "Administrator" or set(roles).intersection(frappe.get_roles(user))))


def require_role(role: str, user: str | None = None) -> None:
    user = user or frappe.session.user
    if not has_role(user, role):
        frappe.throw(_("The current user requires the {0} role.").format(role), frappe.PermissionError)


def require_any_role(roles: set[str] | tuple[str, ...], user: str | None = None) -> None:
    user = user or frappe.session.user
    if not has_any_role(user, roles):
        frappe.throw(_("The current user does not have a required Business Suite role."), frappe.PermissionError)


def ensure_document_permission(doc, permission_type: str = "read") -> None:
    if frappe.session.user == "Guest":
        frappe.throw(_("Authentication is required."), frappe.PermissionError)
    if not frappe.has_permission(doc, permission_type):
        frappe.throw(
            _("You do not have permission to {0} {1}.").format(permission_type, doc.doctype),
            frappe.PermissionError,
        )


def _ensure_role(role_name: str) -> None:
    if not frappe.db.exists("Role", role_name):
        frappe.get_doc({"doctype": "Role", "role_name": role_name, "desk_access": 1, "is_custom": 1}).insert(ignore_permissions=True)


def _permission_exists(doctype: str, role: str) -> bool:
    return bool(frappe.db.exists("DocPerm", {"parent": doctype, "role": role, "permlevel": 0}))


def _upsert_permission(doctype: str, role: str, values: dict) -> None:
    if _permission_exists(doctype, role):
        frappe.db.set_value("DocPerm", {"parent": doctype, "role": role, "permlevel": 0}, values, update_modified=False)
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
    for role in ROLES:
        _ensure_role(role)
    for doctype, role_map in DOCTYPE_PERMISSIONS.items():
        if not frappe.db.exists("DocType", doctype):
            continue
        for role, values in role_map.items():
            _upsert_permission(doctype, role, values)
    frappe.clear_cache()


def has_permission(doc, user=None, permission_type=None):
    user = user or frappe.session.user
    permission_type = permission_type or "read"
    if user == "Administrator" or has_role(user, ROLE_ADMIN):
        return True
    if doc.doctype == "Stock Request":
        if has_any_role(user, (ROLE_MANAGER, ROLE_INVENTORY)):
            return True
        if has_role(user, ROLE_SALES):
            if permission_type in {"read", "write", "create"}:
                return doc.get("requested_by") == user
            return False
    return None


def permission_query_conditions(user=None):
    user = user or frappe.session.user
    if user == "Administrator" or has_role(user, ROLE_ADMIN):
        return ""
    if has_any_role(user, (ROLE_MANAGER, ROLE_INVENTORY)):
        return ""
    return "requested_by = " + frappe.db.escape(user)
