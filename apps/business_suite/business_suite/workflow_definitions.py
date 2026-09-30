"""Framework-independent workflow definitions used by Business Suite."""

from business_suite.role_definitions import (
    ROLE_ADMIN,
    ROLE_INTEGRATION,
    ROLE_INVENTORY,
    ROLE_MANAGER,
    ROLE_SALES,
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
