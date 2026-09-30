#!/usr/bin/env bash
set -Eeuo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
COMPOSE_FILE="$ROOT_DIR/deployment/docker/docker-compose.prod.yml"
ENV_FILE="$ROOT_DIR/deployment/docker/.env.production"
[[ $# -eq 1 ]] || { echo "Usage: $0 <image-tag>"; exit 2; }
TAG="$1"
sed -i.bak -E "s/^CUSTOM_TAG=.*/CUSTOM_TAG=$$TAG/" "$$ENV_FILE"
cd "$$ROOT_DIR"
docker compose --env-file "$$ENV_FILE" -f "$$COMPOSE_FILE" up -d
docker compose --env-file "$$ENV_FILE" -f "$$COMPOSE_FILE" ps
