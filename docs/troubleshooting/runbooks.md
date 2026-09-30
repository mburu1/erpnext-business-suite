# Troubleshooting Runbooks

## App installation failure

Check compatibility, Python environment, Bench registration and migration output.

~~~bash
bench --version
bench list-apps
bench --site <site-name> migrate
bench --site <site-name> clear-cache
~~~

## DocType save/validation failure

Check required fields, server-side validation, permissions and workflow state. Do not rely only on JavaScript validation.

## Slow report

Review filters, date ranges, query shape, indexes, joins and repeated database access. Measure before adding indexes or caching.

## Integration timeout/failure

Check configuration, network reachability, authentication, timeout, provider availability and correlation/request ID. Retry only known transient failures.

## Background job failure

Check worker status, queue backlog, job arguments, worker logs and downstream dependencies.

## Incident record

Capture symptom, impact, timeline, root cause, corrective action and prevention.
