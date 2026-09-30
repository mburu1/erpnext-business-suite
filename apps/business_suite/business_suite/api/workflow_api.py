"""Whitelisted workflow transition endpoints."""

import frappe
from frappe import _

from business_suite.api.common import ensure_permission, success
from business_suite.workflow import transition_document


@frappe.whitelist()
def transition(doctype, name, target_state):
    """Transition a Business Suite document through server-side workflow rules."""
    if doctype not in {"Business Customer", "Stock Request", "Integration Log"}:
        frappe.throw(_("Unsupported workflow DocType."))

    ensure_permission(doctype, "write")
    doc = transition_document(doctype, name, target_state)
    return success(
        name=doc.name,
        doctype=doc.doctype,
        state=doc.get(
            {"Business Customer": "onboarding_status",
             "Stock Request": "status",
             "Integration Log": "status"}[doctype]
        ),
    )
