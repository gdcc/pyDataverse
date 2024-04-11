#!bin/bash

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

# Run all containers
docker compose \
    -f docker/docker-compose-base.yml \
    -f ./docker/docker-compose-test-all.yml \
    --env-file local-test.env \
    up -d

printf "\n🔎 Running pyDataverse tests\n"
printf "   Logs will be printed once finished...\n\n"

# Check if "unit-test" container has finished
while [ -n "$(docker ps -f "name=unit-tests" -f "status=running" -q)" ]; do
    printf "   Waiting for unit-tests container to finish...\n"
    sleep 5
done

# Check if "unit-test" container has failed
if [ "$(docker inspect -f '{{.State.ExitCode}}' unit-tests)" -ne 0 ]; then
    printf "\n❌ Unit tests failed. Printing logs...\n"
    docker logs unit-tests
    printf "\n   Stopping containers\n"
    docker compose \
        -f docker/docker-compose-base.yml \
        -f ./docker/docker-compose-test-all.yml \
        --env-file local-test.env \
        down
    exit 1
fi

# Print test results
printf "\n"
cat dv/unit-tests.log
printf "\n\n✅ Unit tests passed\n\n"

# Stop all containers
docker compose \
    -f docker/docker-compose-base.yml \
    -f ./docker/docker-compose-test-all.yml \
    --env-file local-test.env \
    down
printf "\n🎉 Done\n\n"
