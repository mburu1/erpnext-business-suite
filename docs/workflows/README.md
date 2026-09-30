# Business Suite Workflows

Business Suite workflows are enforced server-side. UI state fields are not trusted as workflow controls.

## Enforced DocTypes

- **Business Customer** — Draft → Verification → Approved/Rejected → Active or Draft.
- **Stock Request** — Draft → Submitted → Manager Review → Approved/Rejected → Fulfilled/Closed.
- **Integration Log** — Queued → Processing → Completed/Failed → Queued for retry when applicable.

## Enforcement

The workflow module defines the legal transition graph and required roles. Each participating DocType calls it from before_save, so invalid transitions cannot be persisted through the UI or normal API writes.

The workflow API exposes an explicit server-side transition endpoint. The endpoint still relies on the same transition graph and role checks.

Every successful persisted state change is recorded in the document timeline with the previous state, target state, and actor.

## Design rule

Business Suite follows:

**RBAC permission → workflow transition validation → business validation → persistence**

A user having write permission does not imply permission to move a document to an arbitrary state.
