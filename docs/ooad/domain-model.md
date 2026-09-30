# Domain Model

~~~text
BusinessCustomer
  +-- onboarding status
  +-- verification
  +-- approval

BusinessProduct
  +-- ERPNext Item reference
  +-- reorder policy
  +-- warehouse preference

StockRequest
  +-- requester
  +-- warehouse
  +-- requested items
  +-- approval state
  +-- fulfillment

IntegrationLog
  +-- request metadata
  +-- outcome
  +-- diagnostics
~~~

## Invariants

### Stock Request
- Quantity is greater than zero.
- Fulfillment requires approval.
- Workflow transitions require the correct role.
- Closed requests are not active work items.

### Customer Onboarding
- Verification precedes approval.
- Approval requires the appropriate role.
- Active customers reference an ERPNext customer master.

### Integration
- Outbound operations have correlation/request IDs.
- Retry behavior prevents duplicate business effects.
- Sensitive values are not written unmasked.
