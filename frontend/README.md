# Business Suite Frontend

Dependency-light vanilla JavaScript UI for the ERPNext/Frappe Business Suite application.

## Architecture

- HTML provides page shells.
- CSS provides responsive layout and reusable components.
- JavaScript modules consume the implemented Business Suite APIs.
- Authentication uses the Frappe session.
- Authorization, validation, workflow transitions, idempotency and integration processing remain server-side.

## Pages

Dashboard, Customers, Customer Detail, Products, Stock Requests, Integrations and Integration Log Detail.

## Deployment

Serve frontend/html through the same origin as the Frappe site. The API client uses relative /api/... URLs and does not hardcode environment-specific hosts or credentials.
