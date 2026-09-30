"""Shared server-side validation helpers for Business Suite DocTypes."""

import frappe
from frappe import _


def require_non_negative(value, label):
    if value is not None and value < 0:
        frappe.throw(_("{0} cannot be negative.").format(label))


def require_positive(value, label):
    if value is None or value <= 0:
        frappe.throw(_("{0} must be greater than zero.").format(label))


def require_existing_link(doctype, name, label):
    if name and not frappe.db.exists(doctype, name):
        frappe.throw(_("{0} {1} does not exist.").format(label, name))


def require_active_business_customer(name):
    if not name:
        return

    customer = frappe.get_cached_doc("Business Customer", name)
    if customer.onboarding_status != "Active":
        frappe.throw(
            _("Business Customer {0} must be Active before it can be used.").format(name)
        )


def require_active_business_product(name):
    if not name:
        return

    product = frappe.get_cached_doc("Business Product", name)
    if not product.active:
        frappe.throw(
            _("Business Product {0} is inactive and cannot be requested.").format(name)
        )
