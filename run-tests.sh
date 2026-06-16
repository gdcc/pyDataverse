#!/usr/bin/env bash
set -euo pipefail

PYTHON_VERSION="${PYTHON_VERSION:-3.11}"

if [[ -z "${API_TOKEN:-}" ]]; then
    echo "API_TOKEN is required."
    exit 1
fi

if [[ -z "${BASE_URL:-}" ]]; then
    echo "BASE_URL is required."
    exit 1
fi

# Usually identical to API_TOKEN, but can be overridden.
API_TOKEN_SUPERUSER="${API_TOKEN_SUPERUSER:-$API_TOKEN}"

CONTAINER_BASE_URL="$BASE_URL"
CONTAINER_BASE_URL="${CONTAINER_BASE_URL//localhost/host.docker.internal}"
CONTAINER_BASE_URL="${CONTAINER_BASE_URL//127.0.0.1/host.docker.internal}"

echo "Building test image with Python ${PYTHON_VERSION}..."
docker build \
    --build-arg PYTHON_VERSION="${PYTHON_VERSION}" \
    -t pydataverse-tests .

echo "Running pytest in container..."
DOCKER_TTY_ARGS=()
if [[ -t 1 ]]; then
    DOCKER_TTY_ARGS=(-it)
fi

docker run --rm \
    "${DOCKER_TTY_ARGS[@]}" \
    --add-host=host.docker.internal:host-gateway \
    -e BASE_URL="${CONTAINER_BASE_URL}" \
    -e API_TOKEN="${API_TOKEN}" \
    -e API_TOKEN_SUPERUSER="${API_TOKEN_SUPERUSER}" \
    pydataverse-tests \
    "$@"
