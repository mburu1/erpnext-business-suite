# Performance & Scalability

The Business Suite performance layer focuses on predictable database work, bounded API responses, short-lived caching, and asynchronous integration processing.

## Implemented controls

### 1. Set-based inventory aggregation

The dashboard previously evaluated stock by loading active products and then issuing a separate `Bin` query for every product. That is an N+1 access pattern.

The dashboard now uses one grouped SQL query joining `tabBusiness Product` to `tabBin`, with the same preferred-warehouse semantics and a deterministic top-10 result.

### 2. Short-lived, permission-scoped dashboard cache

Dashboard responses are cached for 30 seconds using a key scoped to the authenticated Frappe user. This reduces repeated aggregate work while avoiding cross-user sharing of permission-aware responses.

The cache is intentionally short-lived rather than treated as a source of truth. A fresh request after expiry recomputes the aggregates.

### 3. Application indexes

Idempotent indexes are created during `after_install` and `after_migrate` when the corresponding DocType tables exist:

| Table | Index | Purpose |
|---|---|---|
| `tabBusiness Customer` | `idx_bs_customer_onboarding_status` | Status grouping/filtering |
| `tabBusiness Product` | `idx_bs_product_active` | Active-product filtering |
| `tabBusiness Product` | `idx_bs_product_item_warehouse` | Inventory item/warehouse join path |
| `tabStock Request` | `idx_bs_stock_request_status` | Status grouping/filtering |
| `tabIntegration Log` | `idx_bs_integration_log_status` | Integration status reporting |
| `tabIntegration Log` | `idx_bs_integration_log_request_id` | Idempotency/request lookup |

Index creation checks `information_schema` first, so repeated migrations do not attempt to recreate existing indexes.

### 4. Bounded inventory API responses

`get_stock_snapshot` now enforces pagination with a default page size of 100 and a maximum of 500 rows. This prevents an unbounded inventory aggregation response from becoming a memory or network bottleneck.

### 5. Background integration processing

Outbound integrations are already queued through Frappe workers with `enqueue_after_commit=True`. Network I/O therefore does not block the originating HTTP request or transaction.

Integration clients also use separate connect/read timeouts and bounded retries with backoff.

## Performance design rules

1. Prefer set-based SQL or Frappe aggregation over per-record database calls.
2. Every externally callable list/snapshot API must have a bounded page size.
3. Add indexes only for demonstrated filter, grouping, ordering, or join paths.
4. Cache derived dashboard data only when the TTL and authorization scope are explicit.
5. Keep network calls out of synchronous request/transaction paths when they can be queued safely.
6. Keep database names, credentials, URLs, and deployment-specific settings in Frappe/site configuration.
7. Preserve permission checks before returning cached or aggregated data.

## Operational verification

After deploying the app, run a Frappe migration so the index hook executes:

```bash
bench --site <site-name> migrate
```

Then inspect the database execution plan for the dashboard's inventory query with MariaDB `EXPLAIN` when investigating production latency.

For application-level investigation, correlate slow requests using the existing `X-Correlation-Id` response/request header and inspect Frappe worker logs for queued integration jobs.

## Scaling path

The current implementation is intentionally appropriate for a single Frappe site with moderate operational data. If workload grows substantially, the next scaling steps are:

- move high-volume operational reporting to purpose-built aggregate/query tables or reporting jobs;
- introduce scheduled materialization for expensive dashboards;
- separate long-running integrations onto dedicated worker queues;
- monitor MariaDB slow-query logs and query plans before adding further indexes;
- size Redis, web workers, scheduler, and background workers from measured queue/request metrics;
- load-test the highest-volume API and reporting paths against representative data volumes.
