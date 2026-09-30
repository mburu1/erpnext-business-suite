# Observability & Monitoring

This project uses a lightweight, Frappe-native observability layer so production diagnostics do not depend on a mandatory third-party telemetry SDK.

## Signals

### Logs

Every HTTP request emits a structured JSON event through the Frappe logger `business_suite.observability`.

The event contains:

- `event` — `http_request`
- `request_id` — correlation identifier
- `method` and bounded request path
- HTTP status code
- request duration in milliseconds
- slow-request flag
- authenticated Frappe user name

Do not add passwords, tokens, authorization headers, cookies, request bodies, or API credentials to these events. Existing sensitive-data redaction remains the responsibility of integration-specific diagnostics.

### Request correlation

Each request receives a UUID correlation ID. The application returns it as `X-Request-ID` and includes the same value in the structured log event. Support teams can therefore correlate a user-visible error with server-side diagnostics without exposing secrets.

`Server-Timing: app;dur=<milliseconds>` is also emitted when request timing is available, allowing browser and reverse-proxy diagnostics to expose application latency.

### Metrics

The application maintains process-local counters for:

- total requests
- 2xx responses
- 3xx responses
- 4xx responses
- 5xx responses
- slow requests

A request is currently classified as slow at **1,000 ms or more**. These counters are diagnostic, not a replacement for an external metrics backend: Frappe workers are separate processes and their in-memory counters are not globally aggregated.

### Health

The authenticated method:

`business_suite.observability.get_observability_status`

checks database connectivity with `SELECT 1` and returns the database state, request correlation ID, and current process-local counters.

It can be exposed through the standard Frappe method route:

`/api/method/business_suite.observability.get_observability_status`

Keep this endpoint authenticated unless an infrastructure-specific health policy explicitly permits a public health check. If a public probe is required, expose a minimal reverse-proxy or platform health endpoint rather than returning application metrics anonymously.

## Operational monitoring

Recommended production alerts:

| Signal | Suggested action |
|---|---|
| Repeated 5xx responses | Investigate application errors and recent deployments |
| Sustained slow requests | Inspect database queries, external calls, worker saturation, and cache behavior |
| Database health failure | Verify MariaDB/MySQL availability and connection capacity |
| Increasing integration failures | Inspect integration logs, upstream availability, retry exhaustion, and authentication |
| Missing request IDs | Verify application/reverse-proxy header propagation |

Thresholds should be tuned from actual production baselines rather than hard-coded as universal SLOs.

## Log shipping

Frappe's site/application logs remain the primary source. Production deployments should ship application logs to the organization's centralized logging platform, retaining the `request_id` field for correlation.

A typical pipeline is:

```text
Frappe workers
    |
    v
Application logs
    |
    +--> Centralized log store
    |       |
    |       +--> Search by request_id
    |       +--> Error-rate dashboards
    |       +--> Slow-request analysis
    |
    +--> Infrastructure monitoring
            |
            +--> Health checks
            +--> CPU / memory / disk
            +--> Database capacity
            +--> Worker/process saturation
```

## Database and infrastructure signals

Application-level telemetry does not replace infrastructure monitoring. Production monitoring should additionally capture:

- MariaDB/MySQL availability and connection saturation
- query latency and slow-query volume
- Redis/cache availability where deployed
- worker queue depth and worker failures
- CPU, memory, disk and filesystem capacity
- Nginx/reverse-proxy error rates and upstream latency
- backup success/failure
- TLS certificate expiry

## Privacy and security

Observability must not become a data-exfiltration path. Keep logs free of credentials and unnecessary personal or financial data. Restrict access to application logs and monitoring systems according to operational roles, and apply retention periods appropriate to the environment.

## Failure behavior

Observability must be non-blocking. Request diagnostics should not turn a successful business operation into a failure because telemetry itself encountered an exception. The health check is intentionally separate from normal business requests so infrastructure probes can detect database degradation directly.

## Future extension

If centralized metrics/traces become a requirement, OpenTelemetry can be added at the deployment/platform layer without changing business-domain code. The existing request ID, structured log schema, and bounded timing data provide a migration path toward traces and external metrics backends.
