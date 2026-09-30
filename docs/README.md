# Engineering Documentation

This directory contains the design and operational documentation for ERPNext Business Suite.

## Map

- [Architecture](architecture/system-architecture.md)
- [Component boundaries](architecture/component-boundaries.md)
- [ERD](erd/erd.md)
- [Custom DocTypes](erd/custom-doctypes.md)
- [Use cases](ooad/use-cases.md)
- [Domain model](ooad/domain-model.md)
- [Sequence diagrams](ooad/sequence-diagrams.md)
- [Stock request](workflows/stock-request.md)
- [Customer onboarding](workflows/customer-onboarding.md)
- [Integration processing](workflows/integration-processing.md)
- [API contracts](integrations/api-contracts.md)
- [Webhook flows](integrations/webhook-flows.md)
- [Security model](security/security-model.md)
- [Deployment architecture](deployment/deployment-architecture.md)
- [Troubleshooting runbooks](troubleshooting/runbooks.md)

## Principles

1. ERPNext core remains the platform foundation.
2. Custom behavior belongs in the business_suite app.
3. Workflows are explicit and auditable.
4. Integration failures are observable and recoverable.
5. Secrets never belong in source control.
6. Database changes follow the Frappe migration lifecycle.
