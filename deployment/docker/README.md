# Production Docker

The production image extends the pinned ERPNext image and installs the custom business_suite app.

## Build

```bash
docker build --build-arg ERPNEXT_IMAGE=frappe/erpnext:v16.36.0 -t erpnext-business-suite:production -f deployment/docker/Dockerfile .
```

## Validate

```bash
docker compose --env-file deployment/docker/.env.production -f deployment/docker/docker-compose.prod.yml config
```

Do not commit .env.production. Use .env.production.example as the template.
