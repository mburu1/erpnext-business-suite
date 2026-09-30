# Integrations Runbook

## Scope

Use this runbook for failed outbound REST calls, webhook failures, duplicate deliveries, authentication errors, timeouts, and inconsistent integration state.

## 1. Identify the request

Start with the Integration Log and capture:

- request ID / idempotency key
- integration name
- operation
- timestamp
- status and retry count
- HTTP status, if available
- sanitized error message
- correlation ID

Do not copy secrets, bearer tokens, API keys, signed payloads, or full customer-sensitive payloads into incident records.

## 2. Classify the failure

| Failure | Investigation |
|---|---|
| 401/403 | Verify configured credential validity and required downstream permissions |
| 400/422 | Validate request contract and business data |
| 404 | Verify endpoint/version/environment |
| 409 | Check idempotency and existing downstream state before retrying |
| 429 | Respect downstream rate limits and retry-after semantics |
| 5xx | Check downstream availability and bounded retry policy |
| Connect timeout | DNS/network/TLS/firewall path |
| Read timeout | Downstream processing latency |
| Duplicate event | Check idempotency key/request ID and prior Integration Log entry |

## 3. Safe retry policy

Only retry operations that are explicitly safe according to the downstream contract. The application uses bounded retries with backoff for asynchronous integration processing. Do not manually replay a payment, stock movement, or other non-idempotent operation merely because the first response timed out.

## 4. Webhook failures

For incoming webhooks:

1. verify the endpoint is the application-owned webhook path;
2. verify HMAC-SHA256 signature using the configured secret without logging it;
3. verify timestamp/replay policy where applicable;
4. validate payload size and schema;
5. check rate limiting;
6. use the request/idempotency identifier to prevent duplicate processing;
7. inspect Integration Log for the resulting status.

A signature mismatch should not be solved by disabling authentication.

## 5. Queue-backed outbound integration

Because network I/O is intentionally kept out of the originating HTTP transaction, inspect worker queues and Integration Log state before assuming the user-facing request failed.

Follow [Background workers](background-workers.md) for queue diagnosis.

## Verification

A recovered integration must show a successful, correctly correlated Integration Log entry and the expected downstream business state. For duplicate/replayed events, verify that the downstream state changed only once.
