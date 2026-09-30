# Troubleshooting & Runbooks

This section is the operational support layer for the ERPNext Business Suite. It is designed to turn common production symptoms into repeatable diagnosis, safe remediation, verification, and escalation steps.

## Runbook principles

1. **Stabilize first.** Protect data integrity and user access before attempting invasive remediation.
2. **Diagnose from evidence.** Capture the timestamp, site, affected operation, user-facing symptom, correlation/request ID, and relevant logs before changing state.
3. **Prefer reversible actions.** Restart a worker before deleting queues; disable a failing integration before changing business data; take a backup before schema/data repair.
4. **Never expose secrets.** Do not paste API keys, passwords, tokens, cookies, private certificates, or full Authorization headers into tickets or logs.
5. **Verify after remediation.** Every runbook ends with an explicit validation step.
6. **Escalate when evidence is insufficient.** Do not guess at data repair or production configuration.

## Quick triage

| Symptom | Start here | First safe action |
|---|---|---|
| Site unavailable | [Health checks](health-checks.md) | Check web, database, Redis, and workers |
| 5xx/API errors | [Application errors](application-errors.md) | Correlate request ID and inspect application logs |
| Slow pages/reports | [Database & performance](database.md) | Check query duration, worker saturation, and query plan |
| Integration failures | [Integrations](integrations.md) | Inspect Integration Log and request ID; verify endpoint/auth without exposing secrets |
| Jobs stuck | [Background workers](background-workers.md) | Inspect queue depth and failed jobs; restart only the affected worker class |
| Bad deployment | [Rollback](deployment-rollback.md) | Stop rollout, preserve evidence, restore known-good release |

## Standard incident evidence

Capture, where available:

- UTC timestamp and timezone used by the operator
- Frappe site name
- Environment (`development`, `staging`, or `production`)
- affected endpoint, DocType, report, workflow, or integration
- authenticated user/role, without credentials
- `X-Correlation-Id` or equivalent request identifier
- application and worker log excerpts with secrets/redacted personal data removed
- current Git commit/release identifier
- recent deployment or migration activity
- database/Redis/worker health state
- exact error message and traceback, if safe to share

## Runbook index

- [Health checks](health-checks.md)
- [Application errors](application-errors.md)
- [Database & performance](database.md)
- [Integrations](integrations.md)
- [Background workers](background-workers.md)
- [Deployment rollback](deployment-rollback.md)
- [Incident response](incident-response.md)
- [Diagnostic commands](diagnostic-commands.md)

## Change safety

Production changes should follow this sequence:

`Observe -> Capture evidence -> Isolate -> Mitigate -> Verify -> Document -> Prevent recurrence`

For database changes, preserve a backup/recovery path first. For integrations, use idempotent request identifiers and avoid replaying a non-idempotent operation unless the downstream contract explicitly supports it.
