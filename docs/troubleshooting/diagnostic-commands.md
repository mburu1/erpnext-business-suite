# Diagnostic Commands

These commands are intentionally read-heavy and should be adapted to the installed Frappe/ERPNext version and deployment topology.

## Repository/release

```bash
git rev-parse --short HEAD
git status --short
```

## Frappe site

```bash
bench --site <site-name> status
bench --site <site-name> doctor
bench --site <site-name> version
```

## Migration/cache state

```bash
bench --site <site-name> migrate
bench --site <site-name> clear-cache
```

Run `migrate` only as an intentional deployment/repair action, not as a generic diagnostic command on production.

## Logs

Use the deployment's configured log locations and collect a narrow timestamp window. Typical bench environments expose web, worker, scheduler, and error logs under the bench/logs directory.

```bash
cd <frappe-bench>
ls -lah logs/
tail -n 200 logs/*.log
```

Avoid copying entire log files into tickets because they may contain personal or operationally sensitive data.

## Database

```bash
mysql --version
```

Then use an approved MariaDB client/account for read-only diagnostics such as `SHOW FULL PROCESSLIST;` and `EXPLAIN` on the affected query. Never place database passwords in command arguments that may enter shell history.

## Network

```bash
curl -I https://<host>
getent hosts <host>
```

Use `curl` with a controlled endpoint and avoid passing credentials on the command line.

## Diagnostic collection rules

- prefer read-only commands;
- capture timestamps in UTC;
- capture commit/release IDs;
- redact secrets and unnecessary personal data;
- do not run destructive SQL during initial triage;
- do not clear queues before preserving job evidence;
- do not restart all services simultaneously unless the incident commander explicitly chooses that containment action.
