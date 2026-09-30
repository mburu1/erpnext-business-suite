# Use Cases

## Actors

- Employee
- Manager
- Operations User
- CRM User
- Integration Worker
- Administrator
- Business User

## Core use cases

| ID | Use case | Actor |
|---|---|---|
| UC-01 | Create stock request | Employee |
| UC-02 | Review stock request | Manager |
| UC-03 | Fulfill stock request | Operations User |
| UC-04 | Onboard business customer | CRM User |
| UC-05 | Process integration | Integration Worker |
| UC-06 | Review reports | Business User |
| UC-07 | Configure permissions | Administrator |

## Cross-cutting behavior

Mutations should consider authorization, validation, auditability, transaction consistency and safe error handling.
