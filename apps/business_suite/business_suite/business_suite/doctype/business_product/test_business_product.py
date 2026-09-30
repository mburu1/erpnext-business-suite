import frappe
from frappe.tests.utils import FrappeTestCase


class TestBusinessProduct(FrappeTestCase):
    def test_missing_item_is_rejected(self):
        doc = frappe.get_doc(
            {
                "doctype": "Business Product",
                "item_code": "DOES-NOT-EXIST",
                "reorder_level": 0,
            }
        )

        self.assertRaises(frappe.ValidationError, doc.validate)

    def test_negative_reorder_level_is_rejected(self):
        item = frappe.db.get_value("Item", {}, "name")
        if not item:
            self.skipTest("No Item exists in the test database.")

        doc = frappe.get_doc(
            {
                "doctype": "Business Product",
                "item_code": item,
                "reorder_level": -1,
            }
        )

        self.assertRaises(frappe.ValidationError, doc.validate)
