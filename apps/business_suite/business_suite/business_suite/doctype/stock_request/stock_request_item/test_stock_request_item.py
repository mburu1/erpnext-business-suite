import frappe
from frappe.tests.utils import FrappeTestCase


class TestStockRequestItem(FrappeTestCase):
    def test_quantity_must_be_positive(self):
        product = frappe.db.get_value("Business Product", {}, "name")
        if not product:
            self.skipTest("No Business Product exists in the test database.")

        doc = frappe.get_doc(
            {
                "doctype": "Stock Request Item",
                "business_product": product,
                "qty": 0,
            }
        )

        self.assertRaises(frappe.ValidationError, doc.validate)
