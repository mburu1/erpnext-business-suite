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

| From | To | Required role | Condition |
|---|---|---|---|
| Draft | Submitted | Sales, Inventory, Manager, Administrator | Required fields valid |
| Submitted | Manager Review | Manager, Administrator | Request accepted for review |
| Manager Review | Approved | Manager, Administrator | Policy satisfied |
| Manager Review | Rejected | Manager, Administrator | Request declined |
| Approved | Fulfilled | Inventory, Manager, Administrator | Stock available |
| Fulfilled | Closed | Inventory, Manager, Administrator | Fulfillment completed |
| Rejected | Closed | Manager, Administrator | Rejection finalized |

The server rejects skipped states and unauthorized transitions. A new request must start in Draft. Successful transitions are recorded in the document timeline.
