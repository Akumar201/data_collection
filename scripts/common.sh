#!/bin/bash
# Shared setup for the scripts: works on amd64/arm64 with Compose v2 or v1.

DOCKER_ENV_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../docker_env" && pwd)"

export USERNAME=${USERNAME:-$(id -un)}
export DOCKER_UID=${DOCKER_UID:-$(id -u)}
export DOCKER_GID=${DOCKER_GID:-$(id -g)}

if docker compose version &>/dev/null; then
    COMPOSE=(docker compose)
elif command -v docker-compose &>/dev/null; then
    COMPOSE=(docker-compose)
else
    echo "Error: Docker Compose is not installed."
    exit 1
fi

COMPOSE_FILES=(-f "${DOCKER_ENV_DIR}/docker-compose.yml")
if docker info 2>/dev/null | grep -q "Runtimes:.*nvidia"; then
    COMPOSE_FILES+=(-f "${DOCKER_ENV_DIR}/docker-compose.nvidia.yml")
fi

compose() {
    "${COMPOSE[@]}" "${COMPOSE_FILES[@]}" "$@"
}
