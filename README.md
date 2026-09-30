# ERPNext Business Suite

A portfolio-focused **ERPNext / Frappe Framework customization project** that demonstrates how to translate business requirements into maintainable ERP features, custom DocTypes, workflows, reports, dashboards, integrations, and production-ready operational practices.

> **Project focus:** ERPNext customization and extension using Python, JavaScript, HTML/CSS, and MySQL/MariaDB.

## Goals

This project is designed around the responsibilities of an ERPNext / Frappe Developer:

- Customize and extend ERPNext modules.
- Build Frappe applications with Python and JavaScript.
- Design custom DocTypes, fields, permissions, workflows, reports, and dashboards.
- Integrate ERPNext with internal and third-party systems through REST APIs and webhooks.
- Troubleshoot application and integration issues.
- Establish repeatable testing, deployment, logging, and observability practices.
- Improve performance, security, scalability, and maintainability.
- Work from functional requirements and map them into technical ERP workflows.

## Technology Stack

| Area | Technology |
|---|---|
| ERP Platform | ERPNext |
| Application Framework | Frappe Framework |
| Backend | Python |
| Frontend / Client Scripting | JavaScript |
| Markup | HTML5 |
| Styling | CSS3 |
| Database | MySQL / MariaDB |
| APIs | REST / JSON |
| Integrations | REST APIs, Webhooks |
| Reporting | Frappe Query Reports / Script Reports |
| UI | Frappe Desk, ERPNext Workspaces |
| Testing | Python tests, Frappe test utilities |
| Deployment | Docker / Linux / Nginx |
| CI | GitHub Actions |
| Source Control | Git / GitHub |

## CI/CD

GitHub Actions provides layered validation and controlled artifact publication.

### Continuous Integration

- Python compilation and Ruff linting
- Deterministic unit/quality tests
- E2E/integration contract validation
- Repository structure and configuration hygiene checks
- Pull-request and `main` validation
- Concurrency cancellation and job timeouts
- Least-privilege workflow permissions

### CI/CD supply-chain hardening

- `pip-audit` dependency vulnerability scanning
- Gitleaks secret detection
- Actionlint workflow validation
- Dependabot updates for GitHub Actions and Python dependencies
- Immutable Git-SHA production image tags
- OCI provenance and SBOM generation
- Production image build metadata artifacts
- Protected-environment guidance for actual production deployment

The production image workflow publishes to GitHub Container Registry. The SHA-tagged image is the immutable release reference; `production` is a movable channel tag. Actual production deployment remains an explicit controlled operation.

See `docs/deployment/ci-cd-hardening.md` for the complete release, rollback, governance, and supply-chain controls.

## ERP Domain Coverage

The project models workflows around four core ERP areas:

### HR

- Employee records
- Departments
- Leave and attendance workflows
- Employee requests
- HR operational reports

### Accounts

- Customers and suppliers
- Invoices and payment workflows
- Account-related reporting
- Audit-friendly transaction records

### Inventory

- Items and warehouses
- Stock requests
- Inventory movement visibility
- Low-stock reporting
- Inventory dashboards

### CRM

- Leads
- Customers
- Contacts
- Activities
- Customer interaction tracking
- Sales pipeline reporting

## Custom Frappe App

The primary extension app is:

`business_suite`

It provides a clean place for custom business logic without modifying ERPNext core code.

### Planned Custom DocTypes

| DocType | Purpose |
|---|---|
| Business Customer | Extension point for business-specific customer information |
| Business Product | Business-specific product metadata |
| Stock Request | Internal stock request and approval workflow |
| Integration Log | Traceability for external API/webhook activity |

## Planned Workflows

### Stock Request

`Draft -> Submitted -> Manager Review -> Approved -> Fulfilled -> Closed`

### Customer Onboarding

`Draft -> Verification -> Approved -> Active`

### Integration Request

`Queued -> Processing -> Completed / Failed`

Workflow transitions will be permission-aware and auditable.

## Reports

Planned operational reports include:

- Inventory Summary
- Low Stock Analysis
- Sales Performance
- Customer Activity
- Accounts Transaction Summary
- HR Operational Summary
- Integration Failure Report

Reports will be designed for practical operational decisions rather than demonstrating database queries in isolation.

## Dashboards

The dashboard/workspace layer will surface KPIs such as:

- Total customers
- Open opportunities
- Pending stock requests
- Low-stock items
- Sales activity
- Outstanding operational actions
- Integration success/failure rates

## Integrations

The integration layer is intentionally separated from DocType logic.

Planned capabilities:

- REST API clients
- Incoming webhooks
- Outgoing webhooks
- Request/response validation
- Retry handling
- Idempotency considerations
- Integration audit logging
- Failure diagnostics

Example integration boundaries:

`ERPNext -> External CRM`

`ERPNext -> Internal Inventory Service`

`External System -> ERPNext Webhook`

## Security

Security is treated as an application concern rather than only a login concern.

Implemented hardening includes:

- Frappe role-based permissions and DocType permissions
- Server-side authorization and Stock Request ownership enforcement
- Input validation and bounded webhook payloads
- HMAC-SHA256 webhook authentication with constant-time signature comparison
- IP-based endpoint rate limiting for guest webhook ingress
- Restricted, application-owned webhook handler paths
- Security response headers and HTTPS-aware HSTS
- Secrets supplied through environment/site configuration
- No credentials committed to source control
- Sensitive-data masking helper for structured diagnostics
- Integration request auditing and idempotency handling
- Safe error handling

Detailed controls and deployment requirements are documented in `docs/security/hardening.md`.

## Performance and Scalability

Implemented performance controls include:

- Set-based dashboard inventory aggregation to eliminate the previous product-by-product `Bin` query pattern.
- Short-lived, authenticated-user-scoped dashboard caching.
- Idempotent MariaDB indexes for repeated status filters, product/warehouse joins, and integration request lookup.
- Bounded inventory snapshot pagination with a maximum response size.
- Background integration processing through Frappe workers with connect/read timeouts and bounded retries.
- Slow-operation and query-plan investigation guidance.

Detailed implementation and operational guidance is documented in `docs/performance/scalability.md`.

## Testing Strategy

Testing is enforced at multiple levels rather than relying only on end-to-end checks:

```
Unit Tests
    |
    +-- Business rules
    +-- Validation
    +-- Utilities
    +-- RBAC vocabulary
    +-- Workflow policy

Integration Tests
    |
    +-- DocType interactions
    +-- Database behavior
    +-- REST integrations
    +-- Permission enforcement

Workflow Tests
    |
    +-- State transitions
    +-- Permissions
    +-- Failure paths

E2E / Contract Validation
    |
    +-- Integration boundaries
    +-- Authentication behavior
    +-- Optional live HTTP checks

Quality Gates
    |
    +-- Python compilation
    +-- Ruff linting
    +-- Deterministic pytest suite
    +-- Security hardening regression checks
    +-- Performance/scalability regression contracts
    +-- Secret-literal hygiene checks
```

The deterministic quality suite runs in GitHub Actions without requiring a live Frappe site. Frappe-backed tests remain explicit integration tests requiring a configured ERPNext/Frappe environment, so CI does not silently skip them.

## Project Structure

```text
erpnext-business-suite/
|
├── README.md
├── LICENSE
├── .gitignore
├── .editorconfig
├── .env.example
├── pytest.ini
|
├── apps/
│   └── business_suite/
│       ├── business_suite/
│       │   ├── __init__.py
│       │   ├── hooks.py
│       │   ├── modules.txt
│       │   ├── role_definitions.py
│       │   ├── workflow_definitions.py
│       │   ├── security.py
│       │   ├── performance.py
│       │   ├── api/
│       │   ├── business_suite/
│       │   │   ├── doctype/
│       │   │   ├── report/
│       │   │   └── workspace/
│       │   ├── integrations/
│       │   ├── utils/
│       │   └── tests/
│       │
│       └── pyproject.toml
|
├── config/
├── database/
├── frontend/
├── integrations/
├── reports/
├── docs/
├── deployment/
└── .github/
    ├── dependabot.yml
    └── workflows/
```

## Development Approach

The implementation follows a requirement-to-delivery flow:

```text
Business Requirement
        |
        v
Functional Workflow
        |
        v
DocType / Data Model
        |
        v
Permissions + Workflow
        |
        v
Python Server Logic
        |
        v
JavaScript / Desk UX
        |
        v
Reports + Dashboards
        |
        v
Integration / Automation
        |
        v
Testing
        |
        v
Security Hardening
        |
        v
Performance & Scalability
        |
        v
Deployment + Monitoring
```

## Database

The project targets **MySQL/MariaDB**, consistent with the Frappe/ERPNext ecosystem.

Database documentation will cover:

- Core ERPNext relationships
- Custom DocType relationships
- Naming and indexing considerations
- Transaction boundaries
- Reporting query design
- Migration strategy
- Backup and restore considerations

The application should rely on Frappe configuration and site configuration rather than hard-coding database names, hosts, or credentials.

## Configuration

Environment-specific settings belong outside committed secrets.

Use:

`.env.example`

as a reference for local setup, and configure actual values through the appropriate Frappe/site deployment configuration.

Never commit:

- Database passwords
- API keys
- Access tokens
- Production credentials
- Private certificates

## Deployment

The deployment documentation will cover:

1. Frappe/ERPNext environment preparation
2. Database configuration
3. Custom app installation
4. Site configuration
5. Asset/build handling
6. Background workers
7. Nginx/reverse proxy configuration
8. HTTPS
9. Backups
10. Health checks
11. Application logs
12. Rollback procedures

## Documentation

Detailed engineering documentation lives under `docs/`:

- `architecture/` — application architecture and boundaries
- `erd/` — database and relationship documentation
- `ooad/` — object-oriented analysis and design
- `workflows/` — business process definitions
- `integrations/` — API contracts and integration flows
- `security/` — authentication, authorization, data protection, and hardening
- `performance/` — query efficiency, caching, indexing, API bounds, and scaling guidance
- `deployment/` — environment, CI/CD, release, and rollback procedures
- `troubleshooting/` — diagnostics and operational runbooks

## Portfolio Outcomes

The repository is intended to demonstrate practical experience with:

**ERPNext + Frappe + Python + JavaScript + HTML/CSS + MySQL/MariaDB**

while showing the full engineering lifecycle:

`requirements -> design -> implementation -> integration -> testing -> security -> performance -> deployment -> support`

## Roadmap

### Phase 1 — Foundation
- Frappe app structure
- Configuration
- Documentation
- Development environment

### Phase 2 — ERP Customization
- Custom DocTypes
- Fields and validations
- Permissions
- Naming rules

### Phase 3 — Workflows
- Approval workflows
- State transitions
- Role-based actions

### Phase 4 — Reports & Dashboards
- Query reports
- Script reports
- KPI dashboards
- Operational workspaces

### Phase 5 — Integrations
- REST clients
- Webhooks
- Integration logs
- Retry and failure handling

### Phase 6 — Quality, Security & Performance
- Automated tests
- Security review
- HTTP hardening
- Webhook authentication and rate limiting
- Secret hygiene
- Set-based query optimization
- Database indexing
- Bounded API pagination
- Permission-scoped caching
- Performance regression contracts
- Troubleshooting runbooks
- Automated unit and quality gates
- CI/CD supply-chain hardening

### Phase 7 — Deployment
- Docker-based environment
- Nginx
- CI/CD
- Backup and recovery documentation
- Controlled production releases and rollback

## License

This project is intended for learning, portfolio development, and demonstrating ERPNext/Frappe engineering practices.
