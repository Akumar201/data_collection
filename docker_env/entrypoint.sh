#!/bin/bash
set -e  # Exit immediately if a command fails

# Setup ROS 2 environment
source "/opt/ros/$ROS_DISTRO/setup.bash"

# Source the workspace if it exists
if [ -f "/app/install/setup.bash" ]; then
    source "/app/install/setup.bash"
fi


if [ "$ROUTER_MODE" = "true" ]; then
    echo "Starting Zenoh router in router mode..."
    exec /usr/local/bin/zenohd -c /app/config/router_config.json
else
    echo "Router mode disabled. Starting application..."
fi

# Source additional workspaces if they exist
# if [ -f "/app/data_collection_ws/install/setup.bash" ]; then
#     source "/app/data_collection_ws/install/setup.bash"
# fi

# Execute the command passed to the docker run
exec "$@"