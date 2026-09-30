# Tests

Cross-cutting tests live here while DocType-specific tests remain beside their DocType controllers.

## Test levels

### Unit

Deterministic tests that do not require a running Frappe site:

- RBAC role vocabulary
- Workflow transition policy
- Repository quality contracts

### Integration

Frappe-backed tests cover:

- API permission and pagination boundaries
- Integration idempotency and REST client behavior
- Script-report execution smoke tests
- DocType business validation
- Permission enforcement

### Workflow

Workflow tests verify:

- Valid state-transition paths
- Invalid transitions
- Role authorization boundaries
- Failure and retry paths

### E2E / contract

Repository and optional live HTTP checks verify required integration boundaries and authentication behavior. Live checks are enabled with `BUSINESS_SUITE_BASE_URL`.

## CI policy

GitHub Actions always executes the deterministic unit/quality suite. Frappe-backed tests remain separate because they require a configured ERPNext/Frappe site and database rather than being silently skipped by the CI pipeline.
