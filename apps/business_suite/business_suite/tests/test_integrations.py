"""Tests for API and integration boundaries."""

from unittest.mock import patch

from frappe.tests.utils import FrappeTestCase

from business_suite.integrations.clients.rest_client import RestClient
from business_suite.integrations.webhooks.handler import handle_event, verify_signature


class TestIntegrationHandlers(FrappeTestCase):
    @patch(
        "business_suite.integrations.webhooks.handler._webhook_config",
        return_value={"require_signature": False},
    )
    @patch(
        "business_suite.integrations.webhooks.handler.frappe.db.exists",
        return_value="LOG-1",
    )
    def test_duplicate_webhook_is_idempotent(self, exists, config):
        result = handle_event("inventory", {"event": "updated"}, event_id="evt-1")
        exists.assert_called_once_with(
            "Integration Log",
            {"request_id": "evt-1", "direction": "Inbound"},
        )
        self.assertTrue(result["success"])
        self.assertTrue(result["duplicate"])
        self.assertEqual(result["request_id"], "evt-1")

    @patch(
        "business_suite.integrations.webhooks.handler._webhook_config",
        return_value={"secret": "test-secret", "require_signature": True},
    )
    def test_webhook_signature(self, config):
        body = '{"event":"updated"}'
        import hashlib
        import hmac

        signature = hmac.new(
            b"test-secret",
            body.encode(),
            hashlib.sha256,
        ).hexdigest()
        self.assertTrue(
            verify_signature("inventory", body, f"sha256={signature}")
        )

    @patch("business_suite.integrations.clients.rest_client.requests.request")
    def test_rest_client_returns_json(self, request):
        response = request.return_value
        response.status_code = 200
        response.json.return_value = {"ok": True}
        response.headers = {}

        status, payload, duration = RestClient("https://example.test").request(
            "GET", "/health"
        )
        self.assertEqual(status, 200)
        self.assertEqual(payload, {"ok": True})
        self.assertGreaterEqual(duration, 0)
