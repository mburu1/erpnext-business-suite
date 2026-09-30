# Security Hardening

Business Suite uses Frappe's authentication, session management, RBAC, DocType permissions, and workflow permissions as the primary security boundary. The custom app adds defense-in-depth controls around its APIs and integrations.

## Controls implemented

### Authentication and authorization

- Guest access is limited to the provider-facing webhook ingress and health endpoint.
- Business APIs call shared authentication and permission helpers.
- DocType and row-level authorization remain server-side controls; client-side visibility is not treated as authorization.
- Stock Request ownership rules are enforced through `has_permission` and `permission_query_conditions` hooks.

### Webhook security

- Inbound webhooks require HMAC-SHA256 signatures by default.
- Signature comparison uses constant-time comparison.
- Webhook integration names are validated before configuration lookup.
- Event/idempotency identifiers are bounded before database use.
- Request bodies are limited to 1 MiB before JSON parsing and queueing.
- Guest webhook ingress is rate-limited to 30 POST requests per IP per minute; the health endpoint is limited to 60 requests per IP per minute.
- Duplicate inbound events are detected using the integration log request ID.
- Configured handler paths are restricted to `business_suite.integrations.*` and reject double-underscore traversal patterns. Arbitrary module paths must not be accepted from site configuration.

### HTTP security headers

The `after_request` hook adds conservative browser headers:

- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: SAMEORIGIN`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Permissions-Policy` disabling camera, microphone, and geolocation
- `Strict-Transport-Security` when the request is already HTTPS

A Content Security Policy is intentionally not hard-coded here because Frappe Desk and installed ERPNext applications can require deployment-specific script and asset sources. CSP should be configured and tested at the reverse-proxy/site level for each deployment.

### Secrets and logging

- Secrets belong in Frappe site configuration or the deployment secret store, never source control.
- Webhook secrets are read from site configuration and are never returned by the API.
- The `redact_sensitive` helper is available for structured diagnostic data so password, token, API-key, authorization, signature, and private-key fields can be masked before logging.
- Raw webhook bodies and signatures are not written to the Integration Log by the ingress handler.

### Deployment requirements

Production deployments should also:

1. Serve ERPNext exclusively over HTTPS.
2. Keep `site_config.json` outside source control and protect its filesystem permissions.
3. Configure Frappe's site-wide rate limit for the deployment workload.
4. Keep CORS allowlists explicit; do not use a wildcard for authenticated production applications.
5. Disable unnecessary server scripts and integrations.
6. Restrict database and Redis access to the application network.
7. Store backups outside the application host and test restoration.
8. Review Frappe and ERPNext security releases before production upgrades.

## Verification

Security hardening is covered by deterministic tests in `test_security_hardening.py` and the repository quality suite. Live Frappe integration tests remain separate because they require an installed site and configured authentication/database environment.
