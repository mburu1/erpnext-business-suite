# Component Boundaries

| Component | Owns | Avoid |
|---|---|---|
| ERPNext Core | Standard ERP behavior | Custom business edits in core |
| business_suite | Custom DocTypes and rules | Duplicating core masters |
| API layer | Request validation and entry points | Direct database bypass |
| Integration clients | External transport/protocol | Workflow decisions |
| Workflows | State transitions and permissions | HTTP concerns |
| Reports | Read-oriented analytics | Transaction mutations |
| Background jobs | Long-running asynchronous work | Interactive UI logic |
| Database | Persistence | Business orchestration |

## Dependency direction

~~~text
ERPNext / Frappe
       ^
       |
business_suite
  ^    ^    ^
  |    |    |
 API  Domain  Integrations
        |
        v
   Frappe persistence
~~~

## Design constraints

- Keep business rules testable.
- Isolate external failure from core transactions where practical.
- Treat client-side hiding as UX, not authorization.
- Avoid duplicate sources of truth.
- Keep reports read-only.
