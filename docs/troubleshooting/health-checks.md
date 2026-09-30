# Health Checks Runbook

## Purpose

Use this runbook when the ERPNext site is unavailable, intermittently failing, or suspected to have unhealthy dependencies.

## 1. Establish scope

Record:

- site name
- first observed timestamp
- affected URL/API/operation
- whether all users or one role/user is affected
- latest deployment/migration time
- correlation ID, if the request reached the application

## 2. Check application status

From the Frappe bench host:

```bash
cd <frappe-bench>
bench --site <site-name> status
bench --site <site-name> doctor
```

If `status` is unavailable for the installed Frappe version, use the service/process checks documented by the deployment environment rather than inventing a replacement command.

## 3. Check dependencies

Validate, in order:

1. Nginx/reverse proxy
2. Frappe web workers
3. MariaDB/MySQL connectivity
4. Redis cache/queue services
5. background workers
6. scheduler

Do not restart every service at once. Restart the smallest affected component so the failure remains diagnosable.

## 4. HTTP health verification

From a trusted operator host:

```bash
curl -fsS -o /dev/null -w "%{http_code}\n" https://<host>/api/method/frappe.auth.get_logged_user
```

For an authenticated endpoint, use an approved test account/token through the operator's secret-management mechanism. Never place credentials directly in shell history or this runbook.

## 5. Interpret common results

| Result | Likely boundary | Next action |
|---|---|---|
| DNS/TLS failure | Network/reverse proxy | Check DNS, certificate, Nginx |
| 502/504 | Proxy/web worker/upstream | Inspect Nginx and Frappe web logs |
| 500 | Application | Follow [Application errors](application-errors.md) |
| DB connection error | MariaDB/MySQL | Follow [Database & performance](database.md) |
| Requests succeed but jobs do not | Workers/Redis | Follow [Background workers](background-workers.md) |
| Only integration endpoints fail | Integration boundary | Follow [Integrations](integrations.md) |

## 6. Verification

A recovery is not complete until:

- unauthenticated public health behavior is correct;
- a controlled authenticated request succeeds;
- a representative read operation succeeds;
- background queues are processing normally;
- no new critical errors appear in the relevant log window.

Record the verification timestamp and release/commit identifier.
