#!/bin/bash
# Full build-run lifecycle with optional cleanup
# Proceed with building and starting the container
export USERNAME=${USERNAME:-"defaultuser"}
export DOCKER_UID=${DOCKER_UID:-1000}
export DOCKER_GID=${DOCKER_GID:-1000}

echo "USERNAME: ${USERNAME}"
echo "UID: ${DOCKER_UID}"
echo "GID: ${DOCKER_GID}"

# Enable access to X server for local Docker containers.
echo "Enabling X11 access for local Docker containers..."
xhost +local:docker

# Define the path to the config file (replace with actual path)
CONFIG_FILE="../config/config.local.yaml"

# Extract left and right gello serial numbers from YAML file using yq
LEFT_GELLO_SERIAL_NO=$(yq e '.station.gello.left_gello_serial_no' "$CONFIG_FILE")
RIGHT_GELLO_SERIAL_NO=$(yq e '.station.gello.right_gello_serial_no' "$CONFIG_FILE")

# Check if the variables are set correctly
if [ -z "$LEFT_GELLO_SERIAL_NO" ] || [ -z "$RIGHT_GELLO_SERIAL_NO" ]; then
    echo "Error: Could not find left or right gello serial numbers in the config file."
    exit 1
fi

# Print the extracted serial numbers (optional)
echo "Left Gello Serial No: $LEFT_GELLO_SERIAL_NO"
echo "Right Gello Serial No: $RIGHT_GELLO_SERIAL_NO"

# You can now use these serial numbers for further processing in your script
# For example, exporting them as environment variables for later use:
export LEFT_GELLO_SERIAL_NO
export RIGHT_GELLO_SERIAL_NO

# Make sure the serial devices exist before changing permissions
if [ -e "$LEFT_GELLO_SERIAL_NO" ]; then
    echo "Changing permissions for left gello serial device..."
    sudo chmod 666 "$LEFT_GELLO_SERIAL_NO"  # Give read/write permissions to all users
else
    echo "Error: Left Gello device does not exist at $LEFT_GELLO_SERIAL_NO."
fi

if [ -e "$RIGHT_GELLO_SERIAL_NO" ]; then
    echo "Changing permissions for right gello serial device..."
    sudo chmod 666 "$RIGHT_GELLO_SERIAL_NO"  # Give read/write permissions to all users
else
    echo "Error: Right Gello device does not exist at $RIGHT_GELLO_SERIAL_NO."
fi


# Make sure the script has executable permission 
chmod +x /can_activate.sh

# Run the can_activate.sh script to activate can port
echo "Running can_activate.sh..."
./can_activate.sh

# Check if the script ran successfully
if [ $? -eq 0 ]; then
    echo "can_activate.sh ran successfully."
else
    echo "Error: can_activate.sh failed to run."
    exit 1
fi

# Get the absolute path to the project root (one level up from the scripts directory)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DOCKER_ENV_DIR="${PROJECT_ROOT}/docker_env"

# Ensure docker_env directory exists
if [ ! -d "$DOCKER_ENV_DIR" ]; then
    echo "Error: docker_env directory not found at $DOCKER_ENV_DIR"
    exit 1
fi

# Function to stop and remove all running Docker containers
kill_docker_containers() {
    echo "Stopping all running Docker containers..."
    docker ps -q | xargs -r docker stop
    docker ps -aq | xargs -r docker rm
    echo "All containers stopped and removed."
}

# Function to restart Docker containers
restart_docker_containers() {
    echo "Checking if any Docker containers exist..."

    # Check if there are any stopped or running containers
    if [ -z "$(docker ps -aq)" ]; then
        echo "⚠️ No existing Docker containers found to restart. Please build the container first."
        exit 1
    fi

    echo "Restarting Docker containers..."
    cd "$DOCKER_ENV_DIR" || { echo "Failed to enter docker_env directory"; exit 1; }
    docker-compose up -d
    echo "✅ Docker containers restarted successfully."
}

# Prompt user to delete existing Docker images and rebuild from scratch
read -p "Do you want to stop and remove all the existing Docker images and rebuild from scratch? (y/n): " rebuild_confirm
if [ "$rebuild_confirm" = "y" ]; then
    echo "Deleting existing Docker images..."
    kill_docker_containers
    docker rmi data_collection:latest -f
    echo "All Docker images deleted."

    # Checking if the essential environment variables are set
    if [ -z "$USERNAME" ] || [ -z "$DOCKER_UID" ] || [ -z "$DOCKER_GID" ]; then
        echo "Required environment variables are not set."
        exit 1  
    fi

    # Navigate to docker_env directory before executing docker-compose
    cd "$DOCKER_ENV_DIR" || { echo "Failed to enter docker_env directory"; exit 1; }

    # Build the Docker container using the correct build args
    docker-compose build --build-arg USERNAME=${USERNAME} --build-arg UID=${DOCKER_UID} --build-arg GID=${DOCKER_GID} data_collection

    # Start the container in detached mode
    docker-compose up -d
else
    echo "Skipping rebuild. Restarting existing containers..."
    restart_docker_containers
fi
# Attach to the running container using its container name as defined in docker-compose.yml
docker exec -it data_collection_container /bin/bash