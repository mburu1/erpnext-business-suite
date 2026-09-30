# Customer Onboarding Workflow

~~~mermaid
stateDiagram-v2
    [*] --> Draft
    Draft --> Verification
    Verification --> Approved
    Verification --> Rejected
    Approved --> Active
    Rejected --> Draft
~~~

## Transition enforcement

| From | To | Required role |
|---|---|---|
| Draft | Verification | Sales, Manager, Administrator |
| Verification | Approved | Manager, Administrator |
| Verification | Rejected | Manager, Administrator |
| Approved | Active | Manager, Administrator |
| Rejected | Draft | Sales, Manager, Administrator |

The server rejects every transition outside this graph. A new record must start in Draft. Successful transitions are written to the document timeline.
