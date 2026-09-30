# Logical ERD

The custom model augments standard ERPNext masters such as Customer, Item, Warehouse, Employee and User.

~~~mermaid
erDiagram
    BUSINESS_CUSTOMER {
        string name PK
        string customer
        string onboarding_status
        string risk_level
    }
    BUSINESS_PRODUCT {
        string name PK
        string item_code
        decimal reorder_level
        boolean active
    }
    STOCK_REQUEST {
        string name PK
        string requested_by
        string warehouse
        string status
        datetime requested_on
    }
    INTEGRATION_LOG {
        string name PK
        string integration_name
        string direction
        string status
        int http_status
    }
    BUSINESS_CUSTOMER ||--o{ STOCK_REQUEST : requests
    BUSINESS_PRODUCT ||--o{ STOCK_REQUEST : requested_for
    STOCK_REQUEST ||--o{ INTEGRATION_LOG : emits
~~~

## Persistence guidance

- Frappe DocTypes are the application data model.
- Standard ERPNext masters should be linked instead of duplicated.
- Index only measured query patterns.
- Migrations must be repeatable.
- Reporting access should remain read-oriented.
