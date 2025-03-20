#!/bin/bash
set -e  # Exit immediately if a command fails

# Setup ROS 2 environment
source "/opt/ros/$ROS_DISTRO/setup.bash"

# Source the workspace if it exists
if [ -f "/app/install/setup.bash" ]; then
    source "/app/install/setup.bash"
fi

# Source additional workspaces if they exist
# if [ -f "/app/data_collection_ws/install/setup.bash" ]; then
#     source "/app/data_collection_ws/install/setup.bash"
# fi

# Execute the command passed to the docker run
exec "$@"