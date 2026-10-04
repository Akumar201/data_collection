#!/bin/bash
# Optionally rebuild, then start the data_collection container and attach to it.
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

if command -v xhost &>/dev/null && [ -n "$DISPLAY" ]; then
    xhost +local:docker
fi

read -p "Rebuild the image from scratch? (y/n): " rebuild
if [ "$rebuild" = "y" ]; then
    compose down
    compose build --no-cache data_collection || exit 1
fi

compose up -d || exit 1
docker exec -it data_collection_container /bin/bash
