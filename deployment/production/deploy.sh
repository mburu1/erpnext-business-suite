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
: "${ERPNEXT_IMAGE:?Set ERPNEXT_IMAGE}"
: "${CUSTOM_IMAGE:?Set CUSTOM_IMAGE}"
: "${CUSTOM_TAG:?Set CUSTOM_TAG}"
: "${SITE_NAME:?Set SITE_NAME}"

if [[ "$CUSTOM_TAG" == "production" || "$CUSTOM_TAG" == "latest" ]]; then
  if [[ "${ALLOW_MUTABLE_TAG:-false}" != "true" ]]; then
    echo "ERROR: production deployment requires an immutable image tag (Git SHA)." >&2
    echo "Set ALLOW_MUTABLE_TAG=true only for an explicitly controlled non-production operation." >&2
    exit 1
  fi
fi

python3 scripts/production_readiness_audit.py

docker build --build-arg "ERPNEXT_IMAGE=$ERPNEXT_IMAGE" --tag "$CUSTOM_IMAGE:$CUSTOM_TAG" --file deployment/docker/Dockerfile .
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" config >/dev/null
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" up -d db redis-cache redis-queue configurator
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" run --rm create-site
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" up -d
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" ps
