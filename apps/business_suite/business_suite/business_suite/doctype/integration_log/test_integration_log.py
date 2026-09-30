import frappe
from frappe.tests.utils import FrappeTestCase


class TestIntegrationLog(FrappeTestCase):
    def test_http_status_must_be_valid(self):
        doc = frappe.get_doc(
            {
                "doctype": "Integration Log",
                "integration_name": "Unit Test",
                "direction": "Outbound",
                "status": "Processing",
                "http_status": 700,
            }
        )

        self.assertRaises(frappe.ValidationError, doc.validate)

    def test_failed_log_requires_error_code(self):
        doc = frappe.get_doc(
            {
                "doctype": "Integration Log",
                "integration_name": "Unit Test",
                "direction": "Outbound",
                "status": "Failed",
                "processed_at": frappe.utils.now_datetime(),
            }
        )

        self.assertRaises(frappe.ValidationError, doc.validate)
