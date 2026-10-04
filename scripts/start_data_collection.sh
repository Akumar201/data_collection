#!/bin/bash
# Start the data_collection container in the background (builds the image if missing).
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

compose up -d
