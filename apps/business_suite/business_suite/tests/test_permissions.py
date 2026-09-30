"""RBAC and authorization boundary tests."""

from unittest.mock import patch

import frappe
from frappe.tests.utils import FrappeTestCase

from business_suite.api.common import ensure_permission
from business_suite.permissions import (
    DOCTYPE_PERMISSIONS,
    ROLE_ADMIN,
    ROLE_INVENTORY,
    ROLE_MANAGER,
    ROLE_REPORT,
    ROLE_SALES,
    has_permission,
    permission_query_conditions,
)


class TestPermissions(FrappeTestCase):
    def test_role_matrix_contains_required_doctypes(self):
        self.assertEqual(
            {
                "Business Customer",
                "Business Product",
                "Stock Request",
                "Integration Log",
            },
            set(DOCTYPE_PERMISSIONS),
        )

    def test_sales_can_create_and_write_business_customer(self):
        perms = DOCTYPE_PERMISSIONS["Business Customer"][ROLE_SALES]
        self.assertEqual(1, perms["read"])
        self.assertEqual(1, perms["write"])
        self.assertEqual(1, perms["create"])
        self.assertNotIn("delete", perms)

    def test_sales_cannot_write_business_product(self):
        perms = DOCTYPE_PERMISSIONS["Business Product"][ROLE_SALES]
        self.assertEqual(1, perms["read"])
        self.assertNotIn("write", perms)
        self.assertNotIn("create", perms)
        self.assertNotIn("delete", perms)

    def test_report_role_is_read_only(self):
        for doctype in DOCTYPE_PERMISSIONS:
            perms = DOCTYPE_PERMISSIONS[doctype].get(ROLE_REPORT, {})
            if perms:
                self.assertEqual(1, perms["read"])
                self.assertNotIn("write", perms)
                self.assertNotIn("create", perms)
                self.assertNotIn("delete", perms)

    def test_sales_stock_request_is_row_scoped(self):
        with patch(
            "business_suite.permissions.frappe.get_roles",
            return_value=[ROLE_SALES],
        ):
            owned = frappe._dict(
                doctype="Stock Request", requested_by="sales@example.com"
            )
            other = frappe._dict(
                doctype="Stock Request", requested_by="other@example.com"
            )
            self.assertTrue(has_permission(owned, "sales@example.com", "read"))
            self.assertFalse(has_permission(other, "sales@example.com", "read"))
            self.assertTrue(has_permission(owned, "sales@example.com", "write"))
            self.assertFalse(has_permission(other, "sales@example.com", "write"))

    def test_manager_and_inventory_can_access_all_stock_requests(self):
        for role in (ROLE_MANAGER, ROLE_INVENTORY):
            with patch(
                "business_suite.permissions.frappe.get_roles", return_value=[role]
            ):
                doc = frappe._dict(
                    doctype="Stock Request", requested_by="another@example.com"
                )
                self.assertTrue(has_permission(doc, "user@example.com", "read"))
                self.assertTrue(has_permission(doc, "user@example.com", "write"))

    def test_stock_request_query_is_scoped_for_sales(self):
        with patch(
            "business_suite.permissions.frappe.get_roles", return_value=[ROLE_SALES]
        ):
            with patch(
                "business_suite.permissions.frappe.db.escape",
                return_value="'sales@example.com'",
            ):
                condition = permission_query_conditions("sales@example.com")
        self.assertIn("requested_by", condition)
        self.assertIn("sales@example.com", condition)

    def test_guest_api_access_is_rejected(self):
        original_user = frappe.session.user
        try:
            frappe.set_user("Guest")
            self.assertRaises(
                frappe.PermissionError,
                ensure_permission,
                "Business Customer",
                "read",
            )
        finally:
            frappe.set_user(original_user)

    def test_administrator_has_application_override(self):
        doc = frappe._dict(doctype="Business Customer")
        self.assertTrue(has_permission(doc, "Administrator", "read"))
        self.assertTrue(ROLE_ADMIN)
