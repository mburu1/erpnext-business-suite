# E2E / Integration Validation

## Purpose

The validation layer verifies that the Business Suite implementation is internally wired
correctly and can be exercised against a running Frappe/ERPNext site without embedding
environment-specific URLs or credentials in source control.

## Validation levels

1. Repository contract validation
   - Required API and integration boundaries exist.
   - CI executes the E2E/integration validation suite.
   - The validation command is reproducible locally.

2. Live HTTP E2E validation
   - Enabled by setting BUSINESS_SUITE_BASE_URL.
   - Calls the deployed Frappe API over HTTP.
   - Confirms a reachable API response.
   - Confirms protected integration endpoints reject unauthenticated access.

## Local execution

From the repository root:

    python -m pip install pytest
    python scripts/run_e2e_validation.py

To validate a running ERPNext/Frappe site:

    $env:BUSINESS_SUITE_BASE_URL="http://erpnext.local"
    python scripts/run_e2e_validation.py

No credentials are committed. Authentication for additional authenticated scenarios
must be supplied by the runtime environment or a dedicated CI secret.

## CI behavior

The default CI run executes deterministic integration-contract checks. Live E2E tests
are skipped unless BUSINESS_SUITE_BASE_URL is explicitly configured.

This separation keeps pull-request validation deterministic while still providing a
production-like HTTP validation path for staging environments.
