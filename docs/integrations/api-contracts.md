# API Contracts

## API boundary

Business Suite exposes Frappe REST methods under /api/method/business_suite.api.*.

Protected methods use Frappe session or API-key authentication and then enforce DocType permissions. Inbound webhooks are the exception: they may be called as guests only when the configured HMAC signature is valid.

## Protected endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | business_suite.api.customer_api.list_business_customers | Paginated customers |
| GET | business_suite.api.customer_api.get_business_customer | Customer detail |
| GET | business_suite.api.inventory_api.list_business_products | Paginated products |
| GET | business_suite.api.inventory_api.get_stock_snapshot | ERPNext stock balances |
| POST | business_suite.api.crud_api.create_document | Create an allowed custom DocType |
| PUT | business_suite.api.crud_api.update_document | Update an allowed custom DocType |
| DELETE | business_suite.api.crud_api.delete_document | Delete an allowed custom DocType |
| POST | business_suite.api.workflow_api.transition | Server-side workflow transition |
| GET | business_suite.api.integration_api.list_logs | Integration audit log |
| GET | business_suite.api.integration_api.get_log | Integration detail |
| POST | business_suite.api.integration_api.enqueue_sync | Queue outbound integration |
| POST | business_suite.api.integration_api.retry_log | Retry a failed integration |

## Webhook endpoint

POST /api/method/business_suite.api.webhook_api.receive?integration_name=inventory

Required headers:

- X-Event-Id or Idempotency-Key
- X-Business-Suite-Signature: sha256=<hex-hmac>

The signature is HMAC-SHA256 over the exact raw request body using the integration secret stored in site configuration.

## Successful response

~~~json
{
  "success": true,
  "correlation_id": "8d3d...",
  "data": {}
}
~~~

Queued operations additionally return request_id and status.

Never expose stack traces, credentials, authorization headers or secret values to API consumers.
