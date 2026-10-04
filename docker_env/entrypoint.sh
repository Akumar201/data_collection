#!/bin/bash
set -e

source "/opt/ros/$ROS_DISTRO/setup.bash"
if [ -f "/app/data_collection_ws/install/setup.bash" ]; then
    source "/app/data_collection_ws/install/setup.bash"
fi

if [ "$#" -eq 0 ]; then
    exec tail -f /dev/null
else
    exec "$@"
fi
