"""Pure unit tests for the framework-independent RBAC vocabulary."""

from business_suite.role_definitions import (
    ROLE_ADMIN,
    ROLE_INTEGRATION,
    ROLE_INVENTORY,
    ROLE_MANAGER,
    ROLE_REPORT,
    ROLE_SALES,
    ROLES,
)


def test_roles_are_unique_and_non_empty():
    assert len(ROLES) == len(set(ROLES))
    assert all(role.strip() for role in ROLES)


def test_required_roles_are_present():
    assert {
        ROLE_ADMIN,
        ROLE_MANAGER,
        ROLE_SALES,
        ROLE_INVENTORY,
        ROLE_INTEGRATION,
        ROLE_REPORT,
    } == set(ROLES)


def test_role_identifiers_use_stable_business_suite_prefix():
    assert all(role.startswith("Business Suite ") for role in ROLES)
