# Multi-arch base (amd64 + arm64); osrf/ros:humble-desktop is amd64-only
FROM ros:humble-perception

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
    ROS_DOMAIN_ID=200 \
    DEBIAN_FRONTEND=noninteractive

# Create group and user, and give the user sudo privileges without a password
RUN groupadd --gid ${GID} ${USERNAME} && \
    useradd --uid ${UID} --gid ${GID} -m ${USERNAME} && \
    echo "${USERNAME} ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Create app directory and adjust ownership for the non-root user
RUN mkdir -p /app && chown -R ${USERNAME}:${USERNAME} /app

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
    ros-humble-ros2-control \
    ros-humble-ros2-controllers \
    ros-humble-controller-manager \
    iproute2 \
    ethtool \
    can-utils \
    && sudo rm -rf /var/lib/apt/lists/*

# Install Rust non-interactively (-y flag confirms installation)
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y

# Add Cargo's bin directory to the PATH
ENV PATH="/home/${USERNAME}/.cargo/bin:${PATH}"

USER root

# Clone the Zenoh repository and build it in release mode
RUN git clone https://github.com/eclipse-zenoh/zenoh.git /app/zenoh && \
    cd /app/zenoh && \
    cargo build --release && \
    install -m 755 target/release/zenohd /usr/local/bin/zenohd && \
    rm -rf /app/zenoh

USER ${USERNAME}

# Add RealSense repository and key
RUN sudo mkdir -p /etc/apt/keyrings && \
    curl -sSf https://librealsense.realsenseai.com/Debian/librealsenseai.asc | gpg --dearmor | sudo tee /etc/apt/keyrings/librealsenseai.gpg > /dev/null && \
    echo "deb [signed-by=/etc/apt/keyrings/librealsenseai.gpg] https://librealsense.realsenseai.com/Debian/apt-repo $(lsb_release -cs) main" | \
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

COPY entrypoint.sh /entrypoint.sh
RUN sudo chmod +x /entrypoint.sh

WORKDIR /app

# Setting up ros2 environment
ENTRYPOINT ["/entrypoint.sh"]
# Default command (can be overridden)
CMD [ "bash" ]