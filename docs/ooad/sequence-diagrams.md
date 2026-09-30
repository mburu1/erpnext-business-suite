# Sequence Diagrams

## Stock request submission

~~~mermaid
sequenceDiagram
    actor Employee
    participant Desk as Frappe Desk
    participant App as Frappe/App
    participant WF as Workflow
    participant DB as Database
    Employee->>Desk: Submit request
    Desk->>App: Save/Submit
    App->>App: Validate rules
    App->>WF: Check transition
    WF-->>App: Allowed
    App->>DB: Persist
    DB-->>App: Commit
    App-->>Desk: Success
~~~

## Integration processing

~~~mermaid
sequenceDiagram
    participant ERP as ERPNext
    participant Queue as Background Job
    participant Ext as External System
    participant Log as Integration Log
    ERP->>Queue: Enqueue sync
    Queue->>Ext: HTTP request
    Ext-->>Queue: Response
    Queue->>Log: Persist outcome
~~~
