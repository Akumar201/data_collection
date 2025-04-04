#!/bin/bash
# clean_docker_containers.sh
# This script stops all running Docker containers and removes all containers.

# Stop all running containers
if [ "$(docker ps -q)" ]; then
    echo "Stopping running containers..."
    docker stop $(docker ps -q)
else
    echo "No running containers to stop."
fi

# Remove all containers (stopped and exited)
if [ "$(docker ps -aq)" ]; then
    echo "Removing all containers..."
    docker rm $(docker ps -aq)
else
    echo "No containers to remove."
fi
