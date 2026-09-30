"""Tests for Business Suite RBAC definitions and row-level policies."""

from unittest.mock import patch

from frappe.tests.utils import FrappeTestCase

from business_suite import permissions


class TestBusinessSuitePermissions(FrappeTestCase):
    def test_expected_roles_are_defined(self):
        self.assertEqual(len(permissions.ROLES), 6)
        self.assertIn(permissions.ROLE_ADMIN, permissions.ROLES)
        self.assertIn(permissions.ROLE_MANAGER, permissions.ROLES)
        self.assertIn(permissions.ROLE_SALES, permissions.ROLES)
        self.assertIn(permissions.ROLE_INVENTORY, permissions.ROLES)
        self.assertIn(permissions.ROLE_INTEGRATION, permissions.ROLES)
        self.assertIn(permissions.ROLE_REPORT, permissions.ROLES)

    def test_all_business_doctypes_have_rbac(self):
        self.assertEqual(
            set(permissions.DOCTYPE_PERMISSIONS),
            {"Business Customer", "Business Product", "Stock Request", "Integration Log"},
        )

    @patch("business_suite.permissions.frappe.get_roles")
    def test_stock_request_manager_has_global_access(self, get_roles):
        get_roles.return_value = [permissions.ROLE_MANAGER]
        doc = type("Doc", (), {"doctype": "Stock Request", "requested_by": "another@example.com"})()
        self.assertTrue(permissions.has_permission(doc, "manager@example.com", "read"))

    @patch("business_suite.permissions.frappe.get_roles")
    def test_stock_request_owner_can_read(self, get_roles):
        get_roles.return_value = [permissions.ROLE_SALES]
        doc = type("Doc", (), {"doctype": "Stock Request", "requested_by": "sales@example.com"})()
        self.assertTrue(permissions.has_permission(doc, "sales@example.com", "read"))
