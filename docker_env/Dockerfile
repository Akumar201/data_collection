FROM osrf/ros:humble-desktop

# Set non-interactive mode and locale
ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

# Define build arguments with default values
ARG USERNAME=defaultuser
ARG UID=1000
ARG GID=1000

# Set environment variables
ENV LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    TZ=America/Los_Angeles \
    ROS_DOMAIN_ID=200

# Create app directory
RUN mkdir -p /app

# Create group and user, and give the user sudo privileges without a password
RUN groupadd --gid ${GID} ${USERNAME} && \
    useradd --uid ${UID} --gid ${GID} -m ${USERNAME} && \
    echo "${USERNAME} ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Install essential tools and ROS2 Packages (Fixed the command)
RUN apt-get update && apt-get install -y apt-utils \
    python3-pip \
    build-essential \
    nano \
    curl \
    wget \
    python3-colcon-common-extensions \
    ros-humble-ros2-control \
    ros-humble-ros2-controllers \
    ros-humble-controller-manager \
    iproute2 \
    && rm -rf /var/lib/apt/lists/*

# Add RealSense repository and key
RUN mkdir -p /etc/apt/keyrings && \
    curl -sSf https://librealsense.intel.com/Debian/librealsense.pgp | tee /etc/apt/keyrings/librealsense.pgp > /dev/null && \
    echo "deb [signed-by=/etc/apt/keyrings/librealsense.pgp] https://librealsense.intel.com/Debian/apt-repo $(lsb_release -cs) main" | \
    tee /etc/apt/sources.list.d/librealsense.list

# Install RealSense SDK 2.0
RUN apt-get update && apt-get install -y \
    librealsense2-utils \
    librealsense2-dev \
    librealsense2-dbg \
    ros-humble-realsense2-camera \
    ros-humble-tf-transformations \
    ros-humble-rqt-image-view \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt /app/requirements.txt

# Install Python dependencies
RUN pip3 install --no-cache-dir -r /app/requirements.txt

# Set up ROS environment
SHELL ["/bin/bash", "-c"]
RUN echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc

COPY ros2_entrypoint.sh /ros2_entrypoint.sh
RUN chmod +x /ros2_entrypoint.sh

WORKDIR /app

# Setting up ros2 environment
ENTRYPOINT ["/ros2_entrypoint.sh"]
CMD [ "bash" ]
