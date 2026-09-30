# Engineering Documentation Index

This directory is the canonical engineering documentation index for ERPNext Business Suite. Documentation is synchronized with the implemented architecture, ERP workflows, integrations, security controls, performance controls, testing, observability, deployment, and operational runbooks.

## Documentation map

### Architecture
- [System architecture](architecture/system-architecture.md)
- [Component boundaries](architecture/component-boundaries.md)

### Data model / ERD
- [ERD](erd/erd.md)
- [Custom DocTypes](erd/custom-doctypes.md)

### OOAD
- [Use cases](ooad/use-cases.md)
- [Domain model](ooad/domain-model.md)
- [Sequence diagrams](ooad/sequence-diagrams.md)

### Business workflows
- [Stock request](workflows/stock-request.md)
- [Customer onboarding](workflows/customer-onboarding.md)
- [Integration processing](workflows/integration-processing.md)

### APIs / integrations
- [API contracts](integrations/api-contracts.md)
- [Webhook flows](integrations/webhook-flows.md)

### Security
- [Security model](security/security-model.md)
- [RBAC](security/rbac.md)
- [Security hardening](security/hardening.md)

### Performance / scalability
- [Performance and scalability](performance/scalability.md)

### Observability / monitoring
- [Monitoring and observability](observability/monitoring.md)

### Testing / validation
- [E2E and integration validation](testing/e2e-integration-validation.md)

### Deployment / production
- [Deployment architecture](deployment/deployment-architecture.md)
- [Production deployment](deployment/production.md)
- [CI/CD hardening](deployment/ci-cd-hardening.md)

### Troubleshooting / runbooks
- [Runbook index](troubleshooting/runbooks.md)
- [Application errors](troubleshooting/application-errors.md)
- [Background workers](troubleshooting/background-workers.md)
- [Database](troubleshooting/database.md)
- [Deployment rollback](troubleshooting/deployment-rollback.md)
- [Diagnostic commands](troubleshooting/diagnostic-commands.md)
- [Health checks](troubleshooting/health-checks.md)
- [Incident response](troubleshooting/incident-response.md)
- [Integrations](troubleshooting/integrations.md)

## Documentation ownership model

| Area | Canonical location | Change trigger |
|---|---|---|
| Architecture | `docs/architecture/` | Component or boundary changes |
| Data model | `docs/erd/` | DocType, relationship, index, or persistence changes |
| Business behavior | `docs/workflows/` and `docs/ooad/` | Workflow or domain-rule changes |
| Integrations | `docs/integrations/` | API, webhook, retry, or contract changes |
| Security | `docs/security/` | Authorization, validation, secrets, or hardening changes |
| Performance | `docs/performance/` | Query, cache, index, pagination, or scaling changes |
| Observability | `docs/observability/` | Logging, metrics, tracing, alerting, or health changes |
| Testing | `docs/testing/` | Test strategy or validation-boundary changes |
| Deployment | `docs/deployment/` | Release, image, CI/CD, or runtime changes |
| Operations | `docs/troubleshooting/` | Incident, diagnostic, health, or rollback changes |

## Synchronization rules

1. Documentation describes implemented behavior; planned work must be explicitly labeled as planned.
2. Every documentation link in this index must resolve to a committed repository file.
3. New cross-cutting implementation layers must add or update their corresponding documentation before the layer is considered complete.
4. Security, performance, observability, testing, deployment, and troubleshooting changes must update both implementation and operational documentation when behavior changes.
5. The CI documentation validation script checks internal Markdown links and required documentation entries on every CI run.
6. `README.md` remains the portfolio-level overview; this index is the detailed engineering source of truth.

## Validation

Run locally from the repository root:

```bash
python scripts/validate_documentation.py
```

CI executes the same validator so broken internal links and missing documentation entries are detected before merge.
