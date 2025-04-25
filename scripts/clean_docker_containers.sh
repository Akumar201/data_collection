#!/bin/bash
# clean_docker_containers.sh
# This script stops all running Docker containers, removes all containers,
# and optionally prunes the Docker system (removing dangling images, unused volumes, etc.).
#
# WARNING: This script will remove containers and, if confirmed, additional Docker data.
# Use with caution.

# Check if Docker is installed
if ! command -v docker &>/dev/null; then
    echo "Docker is not installed. Please install Docker and try again."
    exit 1
fi

# Stop all running containers
running_containers=$(docker ps -q)
if [ -n "$running_containers" ]; then
    echo "Stopping running containers..."
    docker stop $running_containers
else
    echo "No running containers to stop."
fi

# Remove all containers (stopped and exited)
all_containers=$(docker ps -aq)
if [ -n "$all_containers" ]; then
    echo "Removing all containers..."
    docker rm $all_containers
else
    echo "No containers to remove."
fi

# Ask for user confirmation before performing a system prune
read -p "Do you want to remove all unused data (images, networks, volumes, build cache)? [y/N]: " confirm
if [[ "$confirm" =~ ^[Yy]$ ]]; then
    echo "Pruning Docker system..."
    # The -a flag removes all unused images not just dangling ones and -f forces deletion without additional prompt.
    docker system prune -a -f
    echo "Docker system prune completed."
else
    echo "Skipping Docker system prune."
fi