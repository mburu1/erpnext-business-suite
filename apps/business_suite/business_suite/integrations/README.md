# Integrations

The integration boundary isolates external transport from Business Suite business rules.

## Structure

- `clients/` — protocol and transport clients.
- `services/` — orchestration and audit logging.
- `webhooks/` — inbound event handling.

Configuration is read from Frappe/site configuration. Secrets must not be committed.
