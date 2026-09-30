"""Smoke tests for standard report modules."""

from unittest.mock import patch

from frappe.tests.utils import FrappeTestCase

from business_suite.business_suite.report.customer_activity import customer_activity
from business_suite.business_suite.report.integration_summary import integration_summary
from business_suite.business_suite.report.inventory_summary import inventory_summary
from business_suite.business_suite.report.sales_performance import sales_performance
from business_suite.business_suite.report.stock_request_status import stock_request_status


class TestBusinessSuiteReports(FrappeTestCase):
    @patch("business_suite.business_suite.report.customer_activity.customer_activity.frappe.get_all", return_value=[])
    def test_customer_activity_returns_columns(self, get_all):
        columns, data = customer_activity.execute({})
        self.assertTrue(columns)
        self.assertEqual(data, [])
        get_all.assert_called_once()

    @patch("business_suite.business_suite.report.inventory_summary.inventory_summary.frappe.get_all", return_value=[])
    def test_inventory_summary_returns_columns(self, get_all):
        columns, data = inventory_summary.execute({})
        self.assertTrue(columns)
        self.assertEqual(data, [])
        get_all.assert_called_once()

    @patch("business_suite.business_suite.report.sales_performance.sales_performance.frappe.get_all", return_value=[])
    def test_sales_performance_returns_columns(self, get_all):
        columns, data = sales_performance.execute({})
        self.assertTrue(columns)
        self.assertEqual(data, [])
        get_all.assert_called_once()

    @patch("business_suite.business_suite.report.integration_summary.integration_summary.frappe.get_all", return_value=[])
    def test_integration_summary_returns_columns(self, get_all):
        columns, data = integration_summary.execute({})
        self.assertTrue(columns)
        self.assertEqual(data, [])
        get_all.assert_called_once()

    @patch("business_suite.business_suite.report.stock_request_status.stock_request_status.frappe.get_all", return_value=[])
    def test_stock_request_status_returns_columns(self, get_all):
        columns, data = stock_request_status.execute({})
        self.assertTrue(columns)
        self.assertEqual(data, [])
        get_all.assert_called_once()
