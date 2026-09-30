# API Contracts

## Principles

- JSON request/response
- Explicit authentication
- Input validation
- Stable error envelopes
- Correlation IDs
- Timeouts
- Pagination

## Example request

~~~http
POST /api/method/business_suite.api.integration_api.enqueue_sync
Content-Type: application/json
Authorization: Bearer <token>
X-Correlation-Id: 8d3d...

{
  "integration_name": "inventory",
  "record_id": "REQ-0001"
}
~~~

## Example response

~~~json
{
  "success": true,
  "request_id": "INT-0001",
  "status": "queued"
}
~~~

Never expose stack traces, credentials or secret values to API consumers.
