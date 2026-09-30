import frappe
from frappe.tests.utils import FrappeTestCase


class TestStockRequest(FrappeTestCase):
    def test_items_are_required(self):
        user = frappe.session.user
        warehouse = frappe.db.get_value("Warehouse", {}, "name")
        if not warehouse:
            self.skipTest("No Warehouse exists in the test database.")

        doc = frappe.get_doc(
            {
                "doctype": "Stock Request",
                "requested_by": user,
                "warehouse": warehouse,
                "status": "Draft",
            }
        )

        self.assertRaises(frappe.ValidationError, doc.validate)

    def test_duplicate_products_are_rejected(self):
        warehouse = frappe.db.get_value("Warehouse", {}, "name")
        product = frappe.db.get_value("Business Product", {}, "name")
        if not warehouse or not product:
            self.skipTest("Test requires a Warehouse and Business Product.")

        doc = frappe.get_doc(
            {
                "doctype": "Stock Request",
                "requested_by": frappe.session.user,
                "warehouse": warehouse,
                "status": "Draft",
                "items": [
                    {"business_product": product, "qty": 1},
                    {"business_product": product, "qty": 2},
                ],
            }
        )

        self.assertRaises(frappe.ValidationError, doc.validate)
