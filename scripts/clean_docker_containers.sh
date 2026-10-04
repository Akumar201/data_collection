#!/bin/bash
# Remove the data_collection container, and optionally all unused Docker data.
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

compose down

read -p "Also remove all unused images, networks, volumes and build cache? [y/N]: " confirm
if [[ "$confirm" =~ ^[Yy]$ ]]; then
    docker system prune -a -f
fi
