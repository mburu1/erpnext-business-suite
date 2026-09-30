# Role-Based Access Control

Business Suite uses Frappe's native RBAC model and adds a small application-level policy layer for record ownership.

## Roles

| Role | Responsibility |
|---|---|
| Business Suite Administrator | Full Business Suite administration |
| Business Suite Manager | Operational management across customers, products and stock requests |
| Business Suite Sales User | Customer operations and stock-request creation |
| Business Suite Inventory User | Product and stock-request operations |
| Business Suite Integration User | Integration execution and audit logs |
| Business Suite Report User | Read/report access without transactional write access |

## Enforcement layers

1. DocType permissions — CRUD, report, export and print capabilities are synchronized into DocPerm.
2. API authorization — public API methods call frappe.has_permission() through api/common.py.
3. Row-level policy — Stock Requests are restricted to the requester unless the user is a Manager, Inventory User or Administrator.
4. Report roles — standard reports are limited to the roles that need them.
5. Guest protection — API helpers reject unauthenticated Guest sessions.

## Lifecycle

permissions.sync_rbac() is registered for both installation and migration. It is idempotent so repeated migrations do not create duplicate roles or permission rows.

After deployment:

    bench --site <site> migrate
    bench --site <site> clear-cache

Then assign the appropriate Business Suite role to each user from the Frappe User form.

## Security boundary

RBAC is an authorization boundary, not a replacement for business validation or workflow rules. Status transitions, segregation-of-duties rules and integration-specific authorization remain separate concerns.
