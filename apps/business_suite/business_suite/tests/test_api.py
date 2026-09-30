"""Tests for public API permission boundaries and pagination."""

from unittest.mock import patch

from frappe.tests.utils import FrappeTestCase

from business_suite.api import customer_api, inventory_api


class TestBusinessSuiteAPI(FrappeTestCase):
    @patch("business_suite.api.customer_api.ensure_permission")
    @patch("business_suite.api.customer_api.frappe.get_list")
    def test_customer_list_limits_page_size(self, get_list, ensure_permission):
        get_list.return_value = []

        result = customer_api.list_business_customers(limit_start=-10, limit_page_length=500)

        ensure_permission.assert_called_once_with("Business Customer")
        self.assertEqual(result["success"], True)
        self.assertEqual(result["limit_start"], 0)
        self.assertEqual(result["limit_page_length"], 100)
        get_list.assert_called_once()

    @patch("business_suite.api.inventory_api.ensure_permission")
    @patch("business_suite.api.inventory_api.frappe.get_list")
    def test_product_list_limits_page_size(self, get_list, ensure_permission):
        get_list.return_value = []

        result = inventory_api.list_business_products(limit_page_length=0)

        ensure_permission.assert_called_once_with("Business Product")
        self.assertEqual(result["success"], True)
        self.assertEqual(result["limit_page_length"], 1)
        get_list.assert_called_once()
