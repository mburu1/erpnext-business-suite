# Custom DocTypes

The Business Suite data model is implemented as standard Frappe DocTypes and a child table for stock request lines.

## Core DocTypes

- **Business Customer** — links to ERPNext Customer and stores onboarding metadata.
- **Business Product** — links to ERPNext Item and stores business-specific inventory controls.
- **Stock Request** — internal inventory request with requester, warehouse, approval state and item lines.
- **Integration Log** — records integration metadata and processing outcomes without persisting sensitive payloads.

## Child DocType

- **Stock Request Item** — line-level Business Product and quantity details for Stock Request.

Permissions and workflow rules are intentionally deferred to the next implementation stages.
