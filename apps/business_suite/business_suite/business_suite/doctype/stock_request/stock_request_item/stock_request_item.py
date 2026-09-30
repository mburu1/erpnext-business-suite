import frappe
from frappe import _
from frappe.model.document import Document

from business_suite.utils.validation import (
    require_active_business_product,
    require_non_negative,
    require_positive,
)


class StockRequestItem(Document):
    def validate(self):
        if not self.business_product:
            frappe.throw(_("Business Product is required."))

        require_active_business_product(self.business_product)
        require_positive(self.qty, _("Quantity"))

        if self.uom:
            if not frappe.db.exists("UOM", self.uom):
                frappe.throw(_("UOM {0} does not exist.").format(self.uom))

        if self.qty < 0:
            require_non_negative(self.qty, _("Quantity"))
