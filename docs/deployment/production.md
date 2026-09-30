# Production Deployment

## Architecture

```
Internet -> Host Nginx + TLS -> ERPNext frontend :8080
                              -> backend :8000
                              -> websocket :9000
                              -> MariaDB
                              -> Redis cache/queue
                              -> queue-short / queue-long / scheduler
```

The deployment follows the official Frappe Docker service topology while keeping the custom business_suite app in this repository.

## Initial deployment

```bash
cp deployment/docker/.env.production.example deployment/docker/.env.production
chmod 600 deployment/docker/.env.production
nano deployment/docker/.env.production
chmod +x deployment/production/*.sh
./deployment/production/deploy.sh
./deployment/production/healthcheck.sh
```

## Nginx and TLS

Replace erp.example.com in deployment/nginx/erpnext.conf, install it in host Nginx, validate with nginx -t, then provision TLS with the organization's approved ACME/Certbot process. Never commit private keys or certificates.

## Backups

```bash
./deployment/production/backup.sh
```

Copy backups off-host and periodically perform a restore drill. A backup is only a verified recovery mechanism after a successful restore test.

## Release and rollback

GitHub Actions builds images tagged with the commit SHA and publishes the production tag to GHCR. For controlled releases, use an immutable image tag.

```bash
./deployment/production/rollback.sh <previous-image-tag>
./deployment/production/healthcheck.sh
```

Database migrations are not automatically reversible. For destructive schema changes, restore a compatible database backup or use a forward migration.

## Security

- Keep .env.production outside source control.
- Use long random database and Administrator passwords.
- Do not expose MariaDB or Redis publicly.
- Terminate HTTPS at a trusted reverse proxy.
- Restrict SSH and administrative access.
- Keep Docker, Linux, Frappe and ERPNext patched.
- Do not export logs containing credentials or unnecessary personal data.
