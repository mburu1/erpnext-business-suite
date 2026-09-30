"""Tests for dashboard aggregation helpers."""

from unittest.mock import patch

from frappe.tests.utils import FrappeTestCase

from business_suite.api import dashboard_api


class TestDashboardAPI(FrappeTestCase):
    @patch("business_suite.api.dashboard_api.ensure_permission")
    @patch("business_suite.api.dashboard_api.frappe.db.count", side_effect=[7, 11, 13, 17])
    @patch(
        "business_suite.api.dashboard_api.frappe.get_all",
        side_effect=[
            [{"onboarding_status": "Active", "count": 7}],
            [{"status": "Approved", "count": 11}],
            [{"status": "Completed", "count": 13}],
            [{"name": "BS-PROD-00001", "item_code": "ITEM-001", "reorder_level": 10, "preferred_warehouse": "Main"}],
            [{"actual_qty": 4, "projected_qty": 8}],
        ],
    )
    def test_dashboard_summary_is_aggregated(
        self, get_all, db_count, ensure_permission
    ):
        result = dashboard_api.get_dashboard_summary()

        self.assertTrue(result["success"])
        self.assertEqual(result["data"]["kpis"]["customers"], 7)
        self.assertEqual(result["data"]["kpis"]["active_products"], 17)
        self.assertEqual(result["data"]["kpis"]["stock_requests"], 11)
        self.assertEqual(result["data"]["kpis"]["integration_logs"], 13)
        self.assertEqual(result["data"]["kpis"]["low_stock_items"], 1)
        self.assertEqual(result["data"]["low_stock"][0]["item_code"], "ITEM-001")
        self.assertGreaterEqual(ensure_permission.call_count, 4)
