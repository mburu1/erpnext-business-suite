# Webhook Flows

~~~mermaid
flowchart LR
    X[External System] --> S[HMAC Signature]
    S --> V[Validate JSON]
    V --> I[Idempotency Check]
    I --> Q[Queue Job]
    Q --> P[Business Handler]
    P --> L[Integration Log]
~~~

## Controls

- Validate authenticity with HMAC-SHA256.
- Reject malformed JSON and unsupported payload shapes.
- Accept an external event ID or idempotency key when supplied.
- Detect duplicate delivery before queueing.
- Process expensive business work in a background job.
- Persist integration state and event IDs.
- Minimize logged payload content.
- Never log webhook secrets or authorization headers.
- Return deliberate HTTP statuses for malformed/authentication failures.

A persisted inbound event ID prevents the same event from being queued more than once.
