import frappe
from frappe import _
from frappe.model.document import Document

from business_suite.utils.validation import (
    require_existing_link,
    require_non_negative,
)


class BusinessProduct(Document):
    def validate(self):
        self._validate_item()
        self._validate_category()
        self._validate_reorder_level()
        self._validate_preferred_warehouse()

    def _validate_item(self):
        if not self.item_code:
            frappe.throw(_("Item is required."))

        require_existing_link("Item", self.item_code, _("Item"))

    def _validate_category(self):
        if self.category:
            require_existing_link("Item Group", self.category, _("Item Group"))

    def _validate_reorder_level(self):
        require_non_negative(self.reorder_level, _("Reorder Level"))

    def _validate_preferred_warehouse(self):
        if self.preferred_warehouse:
            require_existing_link(
                "Warehouse", self.preferred_warehouse, _("Preferred Warehouse")
            )
