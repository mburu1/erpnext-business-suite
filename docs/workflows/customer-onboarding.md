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

## Rules

1. Capture required customer information.
2. Complete verification.
3. Restrict approval to authorized roles.
4. Activate only after approval.
5. Preserve verification and approval history.

The custom DocType augments the ERPNext Customer master.
