#!/bin/bash
# build_data_collection.sh
# This script builds the "data_collection" service using a docker-compose file located in ../docker_env/

# Define the path to the docker-compose file
COMPOSE_FILE="../docker_env/docker-compose.yml"

# Check if the docker-compose file exists
if [ ! -f "$COMPOSE_FILE" ]; then
    echo "Error: $COMPOSE_FILE not found."
    exit 1
fi

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "Error: docker-compose is not installed. Please install it and try again."
    exit 1
fi

echo "Building the data_collection service using docker-compose from $COMPOSE_FILE..."
docker-compose -f "$COMPOSE_FILE" build data_collection

if [ $? -eq 0 ]; then
    echo "Successfully built the data_collection service."
else
    echo "Error: Failed to build the data_collection service."
    exit 1
fi