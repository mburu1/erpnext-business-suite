#!/usr/bin/env bash
set -Eeuo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
COMPOSE_FILE="$ROOT_DIR/deployment/docker/docker-compose.prod.yml"
ENV_FILE="$ROOT_DIR/deployment/docker/.env.production"
[[ $# -eq 1 ]] || { echo "Usage: $0 <immutable-git-sha>" >&2; exit 2; }
TAG="$1"

[[ "$TAG" =~ ^[0-9a-f]{40}$ ]] || {
  echo "ERROR: rollback tag must be a 40-character Git commit SHA." >&2
  exit 2
}
[[ -f "$ENV_FILE" ]] || { echo "ERROR: missing $ENV_FILE" >&2; exit 1; }

set -a
source "$ENV_FILE"
set +a
sed -i.bak -E "s/^CUSTOM_TAG=.*/CUSTOM_TAG=$TAG/" "$ENV_FILE"
cd "$ROOT_DIR"
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" pull
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" up -d
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" ps
