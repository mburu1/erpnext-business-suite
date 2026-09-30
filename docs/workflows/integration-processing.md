# Integration Processing Workflow

~~~mermaid
stateDiagram-v2
    [*] --> Queued
    Queued --> Processing
    Processing --> Completed
    Processing --> Failed
    Failed --> Queued : Retryable
    Completed --> [*]
~~~

| From | To | Required role |
|---|---|---|
| Queued | Processing | Integration, Administrator |
| Processing | Completed | Integration, Administrator |
| Processing | Failed | Integration, Administrator |
| Failed | Queued | Integration, Administrator |

## Processing policy

- Generate a correlation/request ID.
- Validate payloads before transmission.
- Use explicit connection/read timeouts.
- Retry only transient failures.
- Use idempotency keys where supported.
- Persist outcome and latency.
- Keep secrets out of logs.
- Enforce the state machine before persistence.
