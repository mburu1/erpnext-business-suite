# System Architecture

ERPNext Business Suite extends ERPNext through a custom Frappe application rather than modifying ERPNext core.

~~~mermaid
flowchart LR
    U[Business Users] --> D[Frappe Desk / ERPNext UI]
    D --> F[Frappe Framework]
    F --> A[business_suite]
    F --> E[ERPNext Core]
    A --> DB[(MariaDB / MySQL)]
    A <--> I[Integration Layer]
    I <--> X[External Systems]
    A --> W[Background Jobs]
~~~

## Runtime layers

### Presentation
Frappe Desk, Workspaces, forms, reports, dashboards, JavaScript, HTML and CSS.

### Application
Custom DocTypes, workflow behavior, server-side validation, APIs and business rules.

### Platform
Frappe ORM/database access, permissions, request handling, jobs and caching.

### ERP domain
ERPNext HR, Accounts, Inventory and CRM capabilities.

### Integration
REST clients, Webhooks, validation, retries, idempotency and integration audit records.

### Persistence
MariaDB/MySQL-compatible site database managed through Frappe migrations.

## Request flow

1. Authenticate the request.
2. Apply role/DocType/workflow permissions.
3. Validate business rules server-side.
4. Persist through Frappe.
5. Queue long-running integration work.
6. Expose read-oriented reports and KPIs.
7. Record integration outcomes.

## Upgrade strategy

Use Frappe extension points, custom DocTypes, hooks and isolated application code instead of editing ERPNext core files. This keeps upgrade coupling visible and supports regression testing.
