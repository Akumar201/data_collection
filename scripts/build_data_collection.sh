#!/bin/bash
# Build the data_collection image.
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

compose build data_collection
