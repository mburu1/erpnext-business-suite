# Stock Request Workflow

~~~mermaid
stateDiagram-v2
    [*] --> Draft
    Draft --> Submitted
    Submitted --> ManagerReview
    ManagerReview --> Approved
    ManagerReview --> Rejected
    Approved --> Fulfilled
    Fulfilled --> Closed
    Rejected --> Closed
~~~

| From | To | Role | Condition |
|---|---|---|---|
| Draft | Submitted | Employee | Required fields valid |
| Submitted | Manager Review | System | Submission accepted |
| Manager Review | Approved | Manager | Policy satisfied |
| Manager Review | Rejected | Manager | Request declined |
| Approved | Fulfilled | Operations | Stock available |
| Fulfilled | Closed | Operations | Fulfillment completed |

Record the actor and transition history for auditability.
