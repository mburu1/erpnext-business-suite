import frappe
from frappe import _
from frappe.model.document import Document

from business_suite.utils.validation import (
    require_active_business_customer,
    require_existing_link,
)


class StockRequest(Document):
    def validate(self):
        self._validate_header()
        self._validate_business_customer()
        self._validate_items()
        self._validate_status_requirements()

    def _validate_header(self):
        if not self.requested_by:
            frappe.throw(_("Requested By is required."))

        if not self.warehouse:
            frappe.throw(_("Warehouse is required."))

        if not self.requested_on:
            self.requested_on = frappe.utils.now_datetime()

        require_existing_link("User", self.requested_by, _("Requested By"))
        require_existing_link("Warehouse", self.warehouse, _("Warehouse"))

    def _validate_business_customer(self):
        if self.business_customer:
            require_active_business_customer(self.business_customer)

    def _validate_items(self):
        if not self.items:
            frappe.throw(_("At least one Stock Request Item is required."))

        seen_products = set()

        for row in self.items:
            if not row.business_product:
                frappe.throw(_("Every Stock Request Item must specify a Business Product."))

            if row.business_product in seen_products:
                frappe.throw(
                    _("Business Product {0} appears more than once in the request.").format(
                        row.business_product
                    )
                )

            seen_products.add(row.business_product)

    def _validate_status_requirements(self):
        if self.status in {"Approved", "Fulfilled", "Closed"} and not self.approved_by:
            frappe.throw(
                _("Approved By is required when Stock Request status is {0}.").format(
                    self.status
                )
            )

        if self.status in {"Fulfilled", "Closed"} and not self.fulfilled_on:
            frappe.throw(
                _("Fulfilled On is required when Stock Request status is {0}.").format(
                    self.status
                )
            )
