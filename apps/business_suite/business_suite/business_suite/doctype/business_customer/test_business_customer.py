import frappe
from frappe.tests.utils import FrappeTestCase


class TestBusinessCustomer(FrappeTestCase):
    def test_approved_status_sets_approver(self):
        customer = self._customer_name()
        if not customer:
            self.skipTest("No Customer exists in the test database.")

        doc = frappe.get_doc(
            {
                "doctype": "Business Customer",
                "customer": customer,
                "onboarding_status": "Approved",
                "risk_level": "Medium",
            }
        )
        doc.validate()
        self.assertEqual(doc.approved_by, frappe.session.user)

    def test_duplicate_customer_is_rejected(self):
        customer = self._customer_name()
        if not customer:
            self.skipTest("No Customer exists in the test database.")

        first = frappe.get_doc(
            {
                "doctype": "Business Customer",
                "customer": customer,
                "onboarding_status": "Draft",
                "risk_level": "Medium",
            }
        )
        first.insert(ignore_permissions=True)

        duplicate = frappe.get_doc(
            {
                "doctype": "Business Customer",
                "customer": customer,
                "onboarding_status": "Draft",
                "risk_level": "Medium",
            }
        )

        self.assertRaises(frappe.ValidationError, duplicate.validate)

    def test_invalid_initial_state_is_rejected_before_save(self):
        customer = self._customer_name()
        if not customer:
            self.skipTest("No Customer exists in the test database.")

        doc = frappe.get_doc(
            {
                "doctype": "Business Customer",
                "customer": customer,
                "onboarding_status": "Approved",
                "risk_level": "Medium",
            }
        )

        self.assertRaises(frappe.ValidationError, doc.before_save)

    def _customer_name(self):
        return frappe.db.get_value("Customer", {}, "name")
