import frappe
from frappe import _
from frappe.model.document import Document


class BusinessCustomer(Document):
    def validate(self):
        self._validate_customer()
        self._validate_status_fields()
        self._validate_duplicate_customer()

    def _validate_customer(self):
        if not self.customer:
            frappe.throw(_("Customer is required."))

    def _validate_status_fields(self):
        if self.onboarding_status in {"Approved", "Active"}:
            if not self.approved_by:
                self.approved_by = frappe.session.user

            if not self.approved_by:
                frappe.throw(
                    _("Approved By is required when the onboarding status is {0}.").format(
                        self.onboarding_status
                    )
                )

    def _validate_duplicate_customer(self):
        if not self.customer:
            return

        filters = {"customer": self.customer}
        if not self.is_new():
            filters["name"] = ["!=", self.name]

        if frappe.db.exists("Business Customer", filters):
            frappe.throw(
                _("Customer {0} already has a Business Customer record.").format(
                    self.customer
                )
            )
