#!/bin/bash
# up_data_collection.sh
# Full build-run lifecycle: optionally rebuild the image, start the container and attach to it.

source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

echo "USERNAME: ${USERNAME}"
echo "UID: ${DOCKER_UID}"
echo "GID: ${DOCKER_GID}"
echo "ARCH: $(uname -m)"

# Enable access to X server for local Docker containers (skipped on headless hosts).
if command -v xhost &>/dev/null && [ -n "$DISPLAY" ]; then
    echo "Enabling X11 access for local Docker containers..."
    xhost +local:docker
fi

# Prompt user to rebuild the image from scratch
read -p "Do you want to remove the existing data_collection container/image and rebuild from scratch? (y/n): " rebuild_confirm
if [ "$rebuild_confirm" = "y" ]; then
    echo "Removing existing data_collection container and image..."
    compose down
    docker rmi data_collection:latest -f

    compose build data_collection || { echo "Error: Failed to build the data_collection service."; exit 1; }
else
    echo "Skipping rebuild. Starting existing container (builds the image if it does not exist)..."
fi

compose up -d || { echo "Error: Failed to start the data_collection service."; exit 1; }
echo "✅ data_collection container is running."

# Attach to the running container using its container name as defined in docker-compose.yml
docker exec -it data_collection_container /bin/bash
