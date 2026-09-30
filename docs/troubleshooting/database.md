# Database & Performance Runbook

## Scope

Use this runbook for slow requests, report timeouts, database errors, lock contention, or unexpectedly high MariaDB resource usage.

## 1. Establish the slow path

Capture:

- endpoint/report/DocType
- correlation ID
- request duration
- timestamp
- approximate data volume
- concurrent workload
- latest migration/index change

Do not immediately add an index based only on one slow request.

## 2. Check application behavior

The project uses set-based inventory aggregation and bounded API pagination. The inventory snapshot should remain bounded by the documented page-size contract. See [Performance & Scalability](../performance/scalability.md).

If a request is slow, determine whether time is spent in:

- Python/application processing
- MariaDB query execution
- Redis/cache access
- external network calls
- queue/worker wait

## 3. Inspect MariaDB

Use an approved database account with the minimum required privileges.

Useful read-only checks include:

```sql
SHOW FULL PROCESSLIST;
SHOW VARIABLES LIKE 'max_connections';
SHOW VARIABLES LIKE 'innodb_lock_wait_timeout';
```

For a specific reporting query, inspect the plan with:

```sql
EXPLAIN <query>;
```

Use `EXPLAIN ANALYZE` only where supported by the installed MariaDB version and where production execution impact is acceptable.

## 4. Common causes

| Symptom | Investigation |
|---|---|
| Many slow dashboard requests | Check aggregation plan, cache behavior, and permission-scoped cache keys |
| Full table scans | Review filters, joins, cardinality, and existing indexes |
| Lock waits | Inspect active transactions and recent write operations |
| Connection exhaustion | Check worker concurrency, long-running queries, and connection configuration |
| Large API response | Verify pagination limits and payload size |

## 5. Index changes

The application already creates idempotent indexes for demonstrated status, join, and integration lookup paths. Before adding another index:

1. reproduce the query;
2. capture the current execution plan;
3. verify the index is not already present;
4. estimate write/storage overhead;
5. add the migration/index through the application's supported deployment path;
6. compare the post-change execution plan.

## 6. Recovery

For lock contention, identify and resolve the offending workload rather than killing arbitrary database sessions. For connection exhaustion, reduce the source of excessive concurrency and investigate leaked/long-lived work before increasing limits.

For suspected corruption or data loss, stop ad-hoc writes and escalate to the approved backup/recovery procedure.

## Verification

Record before/after request duration, query plan, error rate, and resource indicators. A performance fix should be measured against representative data rather than a single small test dataset.
