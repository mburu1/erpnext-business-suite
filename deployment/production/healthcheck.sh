#!/usr/bin/env bash
set -Eeuo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
COMPOSE_FILE="$ROOT_DIR/deployment/docker/docker-compose.prod.yml"
ENV_FILE="$ROOT_DIR/deployment/docker/.env.production"
[[ -f "$ENV_FILE" ]] || { echo "ERROR: missing $ENV_FILE"; exit 1; }
set -a
source "$ENV_FILE"
set +a
cd "$ROOT_DIR"
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" ps
curl --fail --silent --show-error -H "Host: $SITE_NAME" "http://127.0.0.1:${APP_PORT:-8080}/api/method/frappe.auth.get_logged_user" >/dev/null
echo "ERPNext health check passed."
