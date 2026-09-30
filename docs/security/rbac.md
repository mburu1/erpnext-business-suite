# Role-Based Access Control

Business Suite uses Frappe's native RBAC model plus application-level authorization for document boundaries.

## Roles

| Role | Business Customer | Business Product | Stock Request | Integration Log |
|---|---|---|---|---|
| Business Suite Administrator | Full CRUD + report/export/print/email | Full CRUD + report/export/print | Full CRUD + report/export/print | Full CRUD + report/export/print |
| Business Suite Manager | Full CRUD + report/export/print/email | Full CRUD + report/export/print | Full CRUD + report/export/print | Read + report/export/print |
| Business Suite Sales User | Read/write/create + report/export/print/email | Read/report/export/print | Read/write/create + report/print, own-request boundary | No access |
| Business Suite Inventory User | No access | Full CRUD + report/export/print | Read/write/create + report/export/print | No access |
| Business Suite Integration User | No access | No access | No access | Read/write/create + report/export/print |
| Business Suite Report User | Read + report/export/print | Read + report/export/print | Read + report/export/print | Read + report/export/print |

The permission matrix is defined in business_suite/permissions.py and synchronized during after_install and after_migrate.

## Authorization layers

1. Role definitions — Business Suite roles are created idempotently.
2. DocType permissions — the matrix is synchronized to Frappe's native DocPerm records.
3. API authorization — custom API endpoints check authentication and the required DocType/document permission before reading or mutating data.
4. Business-logic authorization — document controllers enforce create/write/delete checks as a second boundary around domain operations.
5. Document-level boundary — Sales users can only read/write/create Stock Requests where requested_by equals the current user. Managers and Inventory users can operate across Stock Requests.
6. List boundary — permission_query_conditions scopes Stock Request list queries for Sales users.
7. Workflow boundary — workflow endpoints check write permission and the workflow layer separately verifies the role allowed to perform each transition.

## CRUD API

business_suite.api.crud_api exposes an allow-listed CRUD boundary for:

- Business Customer
- Business Product
- Stock Request
- Integration Log

It does not accept arbitrary Frappe DocTypes. Read, create, update and delete operations are checked at both DocType and document level before the native document operation runs.

## Security rules

- Guest cannot call Business Suite APIs.
- Administrator is the application superuser.
- Application APIs never use ignore_permissions=True.
- Direct database APIs such as db_insert and db_update are outside this authorization boundary and must not be used for user-driven mutations.
- Workflow authorization and business validation remain separate from RBAC.

## Installation / migration

Run:

    bench --site <site> migrate
    bench --site <site> clear-cache

Then assign Business Suite roles to users through the Frappe User form / Role Permission Manager.

## Verification

Run:

    bench --site <site> run-tests --app business_suite

The authorization suite covers role matrix integrity, CRUD capability boundaries, read-only reporting access, Stock Request row ownership, manager/inventory cross-record access, permission query conditions, Guest API rejection and Administrator access.
