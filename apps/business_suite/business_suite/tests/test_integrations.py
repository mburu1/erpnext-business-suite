"""Tests for integration idempotency and configuration handling."""

from unittest.mock import patch

from frappe.tests.utils import FrappeTestCase

from business_suite.integrations.webhooks.handler import handle_event


class TestIntegrationHandlers(FrappeTestCase):
    @patch("business_suite.integrations.webhooks.handler.frappe.db.exists", return_value="LOG-1")
    def test_duplicate_webhook_is_idempotent(self, exists):
        result = handle_event("inventory", {"event": "updated"}, event_id="evt-1")

        exists.assert_called_once_with(
            "Integration Log",
            {"request_id": "evt-1", "direction": "Inbound"},
        )
        self.assertTrue(result["success"])
        self.assertTrue(result["duplicate"])
        self.assertEqual(result["request_id"], "evt-1")
