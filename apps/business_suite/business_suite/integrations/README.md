# Integrations

The integration boundary isolates external transport from Business Suite business rules.

## Structure

- clients/ — outbound protocol and transport clients.
- services/ — outbound orchestration, retry and audit logging.
- webhooks/ — inbound HMAC authentication, idempotency and asynchronous processing.

## Configuration

Integration definitions live in the Frappe site's site_config.json under business_suite_integrations.

Secrets belong only in real site configuration or a secret-management system. Do not commit credentials, tokens or webhook secrets.

## Reliability controls

- Explicit connection/read timeouts.
- Bounded retries for transient HTTP failures.
- Correlation and idempotency headers.
- Persistent Integration Log records.
- HMAC-SHA256 inbound webhook validation.
- Duplicate webhook detection.
- Background queue processing.
