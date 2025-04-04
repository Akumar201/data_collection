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
    /usr/local/bin/zenohd -c /app/config/router_config.json &
fi

# If a command was provided, execute it; otherwise, run a default command
if [ "$#" -eq 0 ]; then
    exec tail -f /dev/null
else
    exec "$@"
fi