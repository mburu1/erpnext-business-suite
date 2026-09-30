"""State-transition enforcement for Business Suite DocTypes."""

from __future__ import annotations

import frappe
from frappe import _

from business_suite.permissions import (
    ROLE_ADMIN,
    ROLE_INVENTORY,
    ROLE_MANAGER,
    ROLE_SALES,
    ROLE_INTEGRATION,
)

WORKFLOWS = {
    "Business Customer": {
        "field": "onboarding_status",
        "initial": "Draft",
        "transitions": {
            "Draft": {"Verification": {ROLE_ADMIN, ROLE_MANAGER, ROLE_SALES}},
            "Verification": {
                "Approved": {ROLE_ADMIN, ROLE_MANAGER},
                "Rejected": {ROLE_ADMIN, ROLE_MANAGER},
            },
            "Approved": {"Active": {ROLE_ADMIN, ROLE_MANAGER}},
            "Rejected": {"Draft": {ROLE_ADMIN, ROLE_MANAGER, ROLE_SALES}},
        },
    },
    "Stock Request": {
        "field": "status",
        "initial": "Draft",
        "transitions": {
            "Draft": {"Submitted": {ROLE_ADMIN, ROLE_MANAGER, ROLE_SALES, ROLE_INVENTORY}},
            "Submitted": {"Manager Review": {ROLE_ADMIN, ROLE_MANAGER}},
            "Manager Review": {
                "Approved": {ROLE_ADMIN, ROLE_MANAGER},
                "Rejected": {ROLE_ADMIN, ROLE_MANAGER},
            },
            "Approved": {"Fulfilled": {ROLE_ADMIN, ROLE_MANAGER, ROLE_INVENTORY}},
            "Fulfilled": {"Closed": {ROLE_ADMIN, ROLE_MANAGER, ROLE_INVENTORY}},
            "Rejected": {"Closed": {ROLE_ADMIN, ROLE_MANAGER}},
        },
    },
    "Integration Log": {
        "field": "status",
        "initial": "Queued",
        "transitions": {
            "Queued": {"Processing": {ROLE_ADMIN, ROLE_INTEGRATION}},
            "Processing": {
                "Completed": {ROLE_ADMIN, ROLE_INTEGRATION},
                "Failed": {ROLE_ADMIN, ROLE_INTEGRATION},
            },
            "Failed": {"Queued": {ROLE_ADMIN, ROLE_INTEGRATION}},
        },
    },
}


def _has_any_role(user: str, roles: set[str]) -> bool:
    return user == "Administrator" or bool(roles.intersection(frappe.get_roles(user)))


def enforce_transition(doc) -> None:
    """Reject illegal state changes and changes made without the required role."""
    config = WORKFLOWS.get(doc.doctype)
    if not config:
        return

    field = config["field"]
    current = doc.get(field)

    if not current:
        frappe.throw(_("{0} is required.").format(field.replace("_", " ").title()))

    previous_doc = doc.get_doc_before_save()
    if previous_doc is None:
        if current != config["initial"]:
            frappe.throw(
                _("{0} must start in the {1} state.").format(
                    doc.doctype, config["initial"]
                )
            )
        return

    previous = previous_doc.get(field)
    if previous == current:
        return

    allowed = config["transitions"].get(previous, {}).get(current)
    if not allowed:
        frappe.throw(
            _("Invalid {0} transition: {1} -> {2}.").format(
                doc.doctype, previous, current
            )
        )

    user = frappe.session.user
    if not _has_any_role(user, allowed):
        frappe.throw(
            _("The current user is not authorized to transition {0} from {1} to {2}.").format(
                doc.doctype, previous, current
            ),
            frappe.PermissionError,
        )


def record_transition(doc) -> None:
    """Write a human-readable workflow transition to the document timeline."""
    previous_doc = doc.get_doc_before_save()
    if previous_doc is None:
        return

    config = WORKFLOWS.get(doc.doctype)
    if not config:
        return

    field = config["field"]
    previous = previous_doc.get(field)
    current = doc.get(field)
    if previous == current:
        return

    doc.add_comment(
        "Workflow",
        _("State changed from {0} to {1} by {2}.").format(
            previous, current, frappe.session.user
        ),
    )


def transition_document(doctype: str, name: str, target_state: str):
    """Perform a workflow transition through the same server-side rules as the UI."""
    config = WORKFLOWS.get(doctype)
    if not config:
        frappe.throw(_("Workflow is not configured for {0}.").format(doctype))

    doc = frappe.get_doc(doctype, name)
    field = config["field"]
    doc.set(field, target_state)
    doc.save()
    return doc
