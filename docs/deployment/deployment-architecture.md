# Deployment Architecture

~~~mermaid
flowchart LR
    DEV[Development] --> TEST[Test / QA]
    TEST --> PROD[Production]
~~~

## Production topology

~~~text
Internet / Corporate Network
            |
          Nginx
            |
      Frappe / ERPNext
        |           |
        |           +--> Background Workers
        |
        v
     MariaDB/MySQL

ERPNext <--> External / Internal APIs
~~~

## Release sequence

1. Validate source and automated checks.
2. Back up the target site/database.
3. Deploy the custom app.
4. Run Frappe migrations.
5. Refresh/build assets as required.
6. Restart application/workers.
7. Execute smoke tests.
8. Monitor logs and integration health.
9. Keep rollback steps ready.

Environment-specific settings belong in deployment configuration, not source code.
