# Webhook Flows

~~~mermaid
flowchart LR
    X[External System] --> V[Validate]
    V --> I[Idempotency Check]
    I --> Q[Queue Job]
    Q --> P[Business Action]
    P --> L[Integration Log]
~~~

## Controls

- Validate authenticity/signatures when supported.
- Reject malformed payloads.
- Assign event/correlation IDs.
- Detect duplicate delivery.
- Use background jobs for expensive processing.
- Minimize logged payload content.
- Return deliberate HTTP statuses.

A persisted event ID should prevent the same business side effect from being applied twice.
