FROM osrf/ros:humble-desktop

# Set non-interactive mode and locale
ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

# Define build arguments with default values
ARG USERNAME
ARG UID
ARG GID

# Set environment variables
ENV LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    TZ=America/Los_Angeles \
    ROS_DOMAIN_ID=200 \
    DEBIAN_FRONTEND=noninteractive

# Create app directory
RUN mkdir -p /app

# Create group and user, and give the user sudo privileges without a password
RUN groupadd --gid ${GID} ${USERNAME} && \
    useradd --uid ${UID} --gid ${GID} -m ${USERNAME} && \
    echo "${USERNAME} ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Set user for subsequent instructions
USER ${USERNAME}
ENV PATH=/home/${USERNAME}/.local/bin:$PATH
ENV PATH=/usr/local/cuda/bin:$PATH
# Install essential tools and RealSense SDK dependencies
RUN sudo apt-get update && sudo apt-get install -y apt-utils \
    python3-pip \
    build-essential \
    nano \
    curl \
    wget \
    python3-colcon-common-extensions \
    && sudo rm -rf /var/lib/apt/lists/*

# Add RealSense repository and key
RUN sudo mkdir -p /etc/apt/keyrings && \
    curl -sSf https://librealsense.intel.com/Debian/librealsense.pgp | sudo tee /etc/apt/keyrings/librealsense.pgp > /dev/null && \
    echo "deb [signed-by=/etc/apt/keyrings/librealsense.pgp] https://librealsense.intel.com/Debian/apt-repo $(lsb_release -cs) main" | \
    sudo tee /etc/apt/sources.list.d/librealsense.list

# Install RealSense SDK 2.0
RUN sudo apt-get update && sudo apt-get install -y \
    librealsense2-utils \
    librealsense2-dev \
    librealsense2-dbg \
    ros-humble-realsense2-camera \
    ros-humble-tf-transformations \
    ros-humble-rqt-image-view \
    && sudo rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt /app/requirements.txt

# Install Python dependencies
RUN pip3 install --no-cache-dir -r /app/requirements.txt

# Set up ROS environment
SHELL ["/bin/bash", "-c"]
RUN echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc

COPY ros2_entrypoint.sh /ros2_entrypoint.sh
RUN sudo chmod +x /ros2_entrypoint.sh

WORKDIR /app

# Setting up ros2 environment
ENTRYPOINT ["/ros2_entrypoint.sh"]
# Default command (can be overridden)
CMD [ "bash" ]