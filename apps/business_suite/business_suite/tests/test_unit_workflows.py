"""Pure unit tests for workflow policy, independent of a Frappe site."""

from business_suite.role_definitions import (
    ROLE_ADMIN,
    ROLE_INTEGRATION,
    ROLE_INVENTORY,
    ROLE_MANAGER,
    ROLE_SALES,
    ROLES,
)
from business_suite.workflow_definitions import WORKFLOWS


def test_all_managed_workflows_define_an_initial_state_and_field():
    assert set(WORKFLOWS) == {"Business Customer", "Stock Request", "Integration Log"}
    for config in WORKFLOWS.values():
        assert config["field"]
        assert config["initial"]
        assert config["initial"] in config["transitions"]


def test_customer_workflow_has_no_unauthorized_direct_activation():
    transitions = WORKFLOWS["Business Customer"]["transitions"]
    assert "Active" not in transitions["Draft"]
    assert transitions["Approved"]["Active"] == {ROLE_ADMIN, ROLE_MANAGER}


def test_stock_request_requires_manager_review_before_approval():
    transitions = WORKFLOWS["Stock Request"]["transitions"]
    assert "Approved" not in transitions["Submitted"]
    assert transitions["Submitted"]["Manager Review"] == {ROLE_ADMIN, ROLE_MANAGER}
    assert transitions["Manager Review"]["Approved"] == {ROLE_ADMIN, ROLE_MANAGER}


def test_stock_request_fulfillment_requires_inventory_or_manager():
    transitions = WORKFLOWS["Stock Request"]["transitions"]
    assert transitions["Approved"]["Fulfilled"] == {
        ROLE_ADMIN,
        ROLE_MANAGER,
        ROLE_INVENTORY,
    }


def test_integration_failures_can_only_be_requeued_by_integration_roles():
    transitions = WORKFLOWS["Integration Log"]["transitions"]
    assert transitions["Processing"]["Failed"] == {ROLE_ADMIN, ROLE_INTEGRATION}
    assert transitions["Failed"]["Queued"] == {ROLE_ADMIN, ROLE_INTEGRATION}


def test_workflow_role_references_are_known_business_roles():
    referenced_roles = set()
    for config in WORKFLOWS.values():
        for transitions in config["transitions"].values():
            for roles in transitions.values():
                referenced_roles.update(roles)

    assert referenced_roles <= set(ROLES)
    assert ROLE_SALES in referenced_roles
    assert ROLE_MANAGER in referenced_roles
