#!/bin/bash
# Full build-run lifecycle with optional cleanup
# Proceed with building and starting the container
export USERNAME=${USERNAME:-"defaultuser"}
export DOCKER_UID=${DOCKER_UID:-1000}
export DOCKER_GID=${DOCKER_GID:-1000}

echo "USERNAME: ${USERNAME}"
echo "UID: ${DOCKER_UID}"
echo "GID: ${DOCKER_GID}"

# Enable access to X server for local Docker containers.
echo "Enabling X11 access for local Docker containers..."
xhost +local:docker

# Get the absolute path to the project root (one level up from the scripts directory)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DOCKER_ENV_DIR="${PROJECT_ROOT}/docker_env"

# Ensure docker_env directory exists
if [ ! -d "$DOCKER_ENV_DIR" ]; then
    echo "Error: docker_env directory not found at $DOCKER_ENV_DIR"
    exit 1
fi

# Function to stop and remove all running Docker containers
kill_docker_containers() {
    echo "Stopping all running Docker containers..."
    docker ps -q | xargs -r docker stop
    docker ps -aq | xargs -r docker rm
    echo "All containers stopped and removed."
}

# Function to restart Docker containers
restart_docker_containers() {
    echo "Checking if any Docker containers exist..."

    # Check if there are any stopped or running containers
    if [ -z "$(docker ps -aq)" ]; then
        echo "⚠️ No existing Docker containers found to restart. Please build the container first."
        exit 1
    fi

    echo "Restarting Docker containers..."
    cd "$DOCKER_ENV_DIR" || { echo "Failed to enter docker_env directory"; exit 1; }
    docker-compose up -d
    echo "✅ Docker containers restarted successfully."
}

# Prompt user to delete existing Docker images and rebuild from scratch
read -p "Do you want to stop and remove all the existing Docker images and rebuild from scratch? (y/n): " rebuild_confirm
if [ "$rebuild_confirm" = "y" ]; then
    echo "Deleting existing Docker images..."
    kill_docker_containers
    docker rmi data_collection:latest -f
    echo "All Docker images deleted."

    # Checking if the essential environment variables are set
    if [ -z "$USERNAME" ] || [ -z "$DOCKER_UID" ] || [ -z "$DOCKER_GID" ]; then
        echo "Required environment variables are not set."
        exit 1  
    fi

    # Navigate to docker_env directory before executing docker-compose
    cd "$DOCKER_ENV_DIR" || { echo "Failed to enter docker_env directory"; exit 1; }

    # Build the Docker container using the correct build args
    docker-compose build --build-arg USERNAME=${USERNAME} --build-arg UID=${DOCKER_UID} --build-arg GID=${DOCKER_GID} data_collection

    # Start the container in detached mode
    docker-compose up -d
else
    echo "Skipping rebuild. Restarting existing containers..."
    restart_docker_containers
fi
# Attach to the running container using its container name as defined in docker-compose.yml
docker exec -it data_collection_container /bin/bash