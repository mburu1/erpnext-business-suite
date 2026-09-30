#!/usr/bin/env bash
set -Eeuo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
COMPOSE_FILE="$ROOT_DIR/deployment/docker/docker-compose.prod.yml"
ENV_FILE="$ROOT_DIR/deployment/docker/.env.production"
set -a
source "$ENV_FILE"
set +a
cd "$ROOT_DIR"
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" exec -T backend bench --site "$SITE_NAME" backup --with-files
echo "ERPNext backup completed for $SITE_NAME."
