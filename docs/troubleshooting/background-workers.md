# Background Workers Runbook

## Scope

Use this runbook when queued integrations are delayed, scheduled jobs are not executing, or failed jobs accumulate.

## 1. Confirm the symptom

Determine whether the problem affects:

- one queue
- one integration
- all background work
- scheduler jobs
- only newly queued jobs

Record queue/job identifiers and timestamps.

## 2. Inspect worker health

From the bench host:

```bash
cd <frappe-bench>
bench --site <site-name> doctor
bench --site <site-name> show-pending-jobs
```

If a command is not available in the installed Frappe version, use the corresponding documented queue/worker inspection command for that version. Do not assume command names across Frappe releases.

Inspect process/service logs for worker crashes, Redis connection failures, Python exceptions, and repeated retries.

## 3. Safe remediation

- If one worker class is unhealthy, restart only that class.
- If Redis is unhealthy, restore Redis availability before repeatedly restarting workers.
- If a job repeatedly fails, identify the deterministic error before replaying it.
- If an external integration is unavailable, allow the bounded retry policy to operate rather than manually flooding the downstream system.

Do not delete failed jobs or clear queues as a first response; doing so can destroy evidence and business work.

## 4. Stuck job checklist

1. Identify job name/ID.
2. Identify queue and enqueue timestamp.
3. Check worker logs for the same ID/correlation ID.
4. Check Integration Log if the job performs external I/O.
5. Determine whether the operation is idempotent.
6. Fix the root cause.
7. Retry only through the supported mechanism.
8. Verify business state and resulting logs.

## Verification

Confirm that queue depth returns toward normal, new jobs complete within the expected latency, and the failed-job rate does not immediately return. Record the worker restart or configuration change made during remediation.
