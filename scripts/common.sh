#!/bin/bash
# common.sh
# Shared helpers sourced by the other scripts. Works on both x86 and ARM hosts
# with either Docker Compose v2 ("docker compose") or v1 ("docker-compose").

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DOCKER_ENV_DIR="${PROJECT_ROOT}/docker_env"
COMPOSE_FILE="${DOCKER_ENV_DIR}/docker-compose.yml"

# Build args / runtime user; default to the current host user so files in /app stay writable
export USERNAME=${USERNAME:-$(id -un)}
export DOCKER_UID=${DOCKER_UID:-$(id -u)}
export DOCKER_GID=${DOCKER_GID:-$(id -g)}

# Pick the available compose command
if docker compose version &>/dev/null; then
    COMPOSE=(docker compose)
elif command -v docker-compose &>/dev/null; then
    COMPOSE=(docker-compose)
else
    echo "Error: Docker Compose is not installed. Install the docker-compose-plugin and try again."
    exit 1
fi

# Add the NVIDIA GPU override only on hosts that have the NVIDIA runtime
COMPOSE_FILES=(-f "$COMPOSE_FILE")
if docker info 2>/dev/null | grep -q "Runtimes:.*nvidia"; then
    COMPOSE_FILES+=(-f "${DOCKER_ENV_DIR}/docker-compose.nvidia.yml")
fi

compose() {
    "${COMPOSE[@]}" "${COMPOSE_FILES[@]}" "$@"
}
