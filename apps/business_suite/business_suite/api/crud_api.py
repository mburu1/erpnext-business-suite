"""Explicit, permission-aware CRUD API boundary for Business Suite DocTypes."""

import frappe
from frappe import _

from business_suite.api.common import (
    ensure_allowed_doctype,
    ensure_document_permission,
    ensure_permission,
    parse_payload,
    success,
)

ALLOWED_DOCTYPES = {
    "Business Customer",
    "Business Product",
    "Stock Request",
    "Integration Log",
}


@frappe.whitelist()
def get_document(doctype, name):
    ensure_allowed_doctype(doctype, ALLOWED_DOCTYPES)
    if not name:
        frappe.throw(_("Document name is required."), frappe.ValidationError)

    doc = frappe.get_doc(doctype, name)
    ensure_document_permission(doc, "read")
    return success(doc.as_dict())


@frappe.whitelist()
def create_document(doctype, data):
    ensure_allowed_doctype(doctype, ALLOWED_DOCTYPES)
    ensure_permission(doctype, "create")

    payload = parse_payload(data)
    payload["doctype"] = doctype

    if doctype == "Stock Request" and not payload.get("requested_by"):
        payload["requested_by"] = frappe.session.user

    doc = frappe.get_doc(payload)
    ensure_document_permission(doc, "create")
    doc.insert()
    return success(doc.as_dict())


@frappe.whitelist()
def update_document(doctype, name, data):
    ensure_allowed_doctype(doctype, ALLOWED_DOCTYPES)
    if not name:
        frappe.throw(_("Document name is required."), frappe.ValidationError)

    doc = frappe.get_doc(doctype, name)
    ensure_document_permission(doc, "write")

    payload = parse_payload(data)
    forbidden = {"doctype", "name", "owner", "creation", "modified", "modified_by"}
    for fieldname, value in payload.items():
        if fieldname not in forbidden:
            doc.set(fieldname, value)

    doc.save()
    return success(doc.as_dict())


@frappe.whitelist()
def delete_document(doctype, name):
    ensure_allowed_doctype(doctype, ALLOWED_DOCTYPES)
    if not name:
        frappe.throw(_("Document name is required."), frappe.ValidationError)

    doc = frappe.get_doc(doctype, name)
    ensure_document_permission(doc, "delete")
    doc.delete()
    return success(name=name, doctype=doctype)
