#!/bin/bash
# start_data_collection.sh
# This script starts the "data_collection" service in the background (builds it first if needed).

source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

echo "Starting the data_collection service using ${COMPOSE[*]} from $COMPOSE_FILE..."

if compose up -d; then
    echo "Successfully started the data_collection service."
else
    echo "Error: Failed to start the data_collection service."
    exit 1
fi
