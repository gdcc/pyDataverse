#!/bin/bash

# Parse arguments
usage() {
    echo "Usage: $0 [-p Python version (e.g. 3.10, 3.11, ...)]" 1>&2
    exit 1
}

while getopts ":p:d:" o; do
    case "${o}" in
    p)
        p=${OPTARG}
        ;;
    *) ;;
    esac
done
shift $((OPTIND - 1))

# Fall back to Python 3.11 if no Python version is specified
if [ -z "${p}" ]; then
    printf "\n⚠️  No Python version specified falling back to '3.11'\n"
    p=3.11
fi

# Validate Python version
if [[ ! "${p}" =~ ^3\.[0-9]+$ ]]; then
    echo "\n❌ Invalid Python version. Please specify a valid Python version (e.g. 3.10, 3.11, ...)\n"
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &>/dev/null; then
    echo "✋ Docker is not installed. Please install Docker before running this script."
    exit 1
fi

# Prepare the environment for the test
mkdir dv >>/dev/null 2>&1
touch dv/bootstrap.exposed.env >>/dev/null 2>&1

# Add python version to the environment
export PYTHON_VERSION=${p}

printf "\n🚀 Preparing containers\n"
printf "   Using PYTHON_VERSION=${p}\n\n"

# Start all containers (infrastructure + tests)
printf "\n🚀 Starting all containers...\n"
printf "   The test container will wait for Dataverse and fetch the version automatically\n\n"

docker compose \
    -f docker/docker-compose-base.yml \
    -f ./docker/docker-compose-test-all.yml \
    --env-file local-test.env \
    up -d

printf "\n🔎 Running pyDataverse tests\n"
printf "   Test container will handle version detection and testing...\n\n"

# Check if "unit-test" container has finished
WAIT_COUNT=0
while [ -n "$(docker ps -f "name=unit-tests" -f "status=running" -q)" ]; do
    WAIT_COUNT=$((WAIT_COUNT + 1))
    printf "   ⏳ Waiting for tests to complete... (${WAIT_COUNT})\n"
    sleep 5
done

# Check if "unit-test" container has failed
EXIT_CODE=$(docker inspect -f '{{.State.ExitCode}}' unit-tests 2>/dev/null)

if [ -z "$EXIT_CODE" ]; then
    printf "\n❌ Unit tests container not found or failed to start\n"
    EXIT_CODE=1
else
    printf "\n📋 Unit tests completed with exit code: ${EXIT_CODE}\n"
fi

# Capture Dataverse logs after tests complete
printf "\n📝 Capturing Dataverse logs...\n"
docker logs dataverse > dv/dataverse-logs.log 2>&1

if [ "${EXIT_CODE}" -ne 0 ]; then
    printf "\n❌ Unit tests failed. Showing test results...\n\n"
    printf "=== PYTEST OUTPUT ===\n"
    if [ -f "dv/unit-tests.log" ]; then
        cat dv/unit-tests.log
    else
        printf "⚠️  Test log file not found, showing container logs instead:\n"
        docker logs unit-tests
    fi
    printf "\n=== END PYTEST OUTPUT ===\n"

    
    printf "\n🧹 Stopping containers...\n"
    docker compose \
        -f docker/docker-compose-base.yml \
        -f ./docker/docker-compose-test-all.yml \
        --env-file local-test.env \
        down
    exit 1
fi

# Print test results
printf "\n✅ Unit tests passed! Showing results...\n\n"
printf "=== PYTEST RESULTS ===\n"
if [ -f "dv/unit-tests.log" ]; then
    cat dv/unit-tests.log
else
    printf "⚠️  Test log file not found, showing container logs:\n"
    docker logs unit-tests
fi
printf "\n=== END PYTEST RESULTS ===\n"

# Stop all containers
printf "\n🧹 Stopping containers...\n"
docker compose \
    -f docker/docker-compose-base.yml \
    -f ./docker/docker-compose-test-all.yml \
    --env-file local-test.env \
    down
printf "\n🎉 Done\n\n"
