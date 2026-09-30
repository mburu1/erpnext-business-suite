#!/usr/bin/env bash
set -Eeuo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
COMPOSE_FILE="$ROOT_DIR/deployment/docker/docker-compose.prod.yml"
ENV_FILE="$ROOT_DIR/deployment/docker/.env.production"
[[ -f "$ENV_FILE" ]] || { echo "ERROR: create $ENV_FILE first."; exit 1; }
command -v docker >/dev/null || { echo "ERROR: Docker is required."; exit 1; }
docker compose version >/dev/null || { echo "ERROR: Docker Compose v2 is required."; exit 1; }
cd "$ROOT_DIR"
set -a
source "$ENV_FILE"
set +a
docker build --build-arg "ERPNEXT_IMAGE=$ERPNEXT_IMAGE" --tag "$CUSTOM_IMAGE:$CUSTOM_TAG" --file deployment/docker/Dockerfile .
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" config >/dev/null
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" up -d db redis-cache redis-queue configurator
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" run --rm create-site
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" up -d
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" ps
