# Custom DocTypes

## Business Customer

Links to the standard ERPNext Customer and holds business-specific onboarding data.

Suggested fields:
- customer
- onboarding_status
- segment
- risk_level
- verification_notes
- approved_by

## Business Product

Extends the ERPNext Item with business-specific product controls.

Suggested fields:
- item_code
- category
- reorder_level
- preferred_warehouse
- active

## Stock Request

Models controlled internal inventory requests.

Suggested fields:
- requested_by
- warehouse
- priority
- request_date
- status
- items
- approved_by
- fulfilled_on

## Integration Log

Provides traceability for external/internal integration activity.

Suggested fields:
- integration_name
- direction
- endpoint
- request_id
- status
- http_status
- error_code
- duration_ms
- processed_at

Sensitive payloads must be minimized or masked.
