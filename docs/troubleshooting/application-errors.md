# Application Errors Runbook

## Scope

Use this runbook for HTTP 4xx/5xx responses, Python exceptions, failed DocType operations, permission errors, and unexpected application behavior.

## Triage sequence

### 1. Classify the failure

- **4xx**: validate authentication, authorization, input shape, workflow state, and endpoint contract.
- **5xx**: inspect the application traceback and dependency failures.
- **Timeout**: distinguish application CPU/DB work from external network I/O.
- **Permission failure**: confirm the authenticated role and document ownership rules before changing permissions.
- **Workflow failure**: verify the current document state and allowed transition rather than forcing a state in the database.

### 2. Correlate the request

Use the `X-Correlation-Id` request/response value where present. Search application and worker logs for the same identifier and timestamp.

Do not disclose raw Authorization headers, session cookies, webhook secrets, or other credentials while collecting evidence.

### 3. Check recent changes

Compare the failure timestamp with:

- application deployment
- Frappe migration
- DocType/schema changes
- permission/role changes
- integration configuration changes
- worker or Redis changes

### 4. Safe remediation

Prefer the least invasive corrective action:

1. retry only when the operation is documented as safe/idempotent;
2. correct invalid configuration;
3. restart the affected worker/service if evidence indicates process failure;
4. roll back a known-bad release when a deployment regression is established;
5. restore data only through an approved recovery procedure.

Never directly edit Frappe transactional tables to bypass validation or workflow rules without an explicit, reviewed recovery procedure.

## Common patterns

### `PermissionError` / permission denied

Check the user's roles, DocType permissions, document ownership/share rules, and server-side authorization. Do not solve an application bug by granting Administrator access.

### `DoesNotExistError`

Verify the document name and site. Determine whether the record was deleted, renamed, or never existed. For integrations, verify idempotency/retry behavior before replaying a request.

### Database exceptions

Capture the exact database error, query/report context, and timestamp. Follow [Database & performance](database.md) before changing indexes or schema.

### External API timeout

Determine whether the failure is connect timeout, read timeout, DNS/TLS failure, or downstream HTTP error. Follow [Integrations](integrations.md).

## Verification

After remediation, repeat the smallest representative operation, then validate the surrounding workflow. Confirm that the same error does not recur during a short observation window.
