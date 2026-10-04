#!/bin/bash
# build_data_collection.sh
# This script builds the "data_collection" image. Can be run from any directory.

source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

echo "Building the data_collection service using ${COMPOSE[*]} from $COMPOSE_FILE..."
echo "USERNAME: ${USERNAME}  UID: ${DOCKER_UID}  GID: ${DOCKER_GID}  ARCH: $(uname -m)"

if compose build data_collection; then
    echo "Successfully built the data_collection service."
else
    echo "Error: Failed to build the data_collection service."
    exit 1
fi
