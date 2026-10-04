# Multi-arch base (amd64 + arm64)
FROM ros:humble-perception

ARG USERNAME=defaultuser
ARG UID=1000
ARG GID=1000

ENV LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    TZ=America/Los_Angeles \
    ROS_DOMAIN_ID=200 \
    DEBIAN_FRONTEND=noninteractive

RUN groupadd --gid ${GID} ${USERNAME} && \
    useradd --uid ${UID} --gid ${GID} -m ${USERNAME} && \
    echo "${USERNAME} ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers && \
    mkdir -p /app && chown ${USERNAME}:${USERNAME} /app

RUN mkdir -p /etc/apt/keyrings && \
    curl -sSf https://librealsense.realsenseai.com/Debian/librealsenseai.asc | gpg --dearmor > /etc/apt/keyrings/librealsenseai.gpg && \
    echo "deb [signed-by=/etc/apt/keyrings/librealsenseai.gpg] https://librealsense.realsenseai.com/Debian/apt-repo $(lsb_release -cs) main" \
    > /etc/apt/sources.list.d/librealsense.list && \
    apt-get update && apt-get install -y \
    python3-pip \
    python3-colcon-common-extensions \
    build-essential \
    nano \
    iproute2 \
    ethtool \
    can-utils \
    librealsense2-utils \
    librealsense2-dev \
    ros-humble-realsense2-camera \
    ros-humble-rqt-image-view \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

USER ${USERNAME}
ENV PATH=/home/${USERNAME}/.local/bin:$PATH
RUN echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc

WORKDIR /app
ENTRYPOINT ["/entrypoint.sh"]
CMD ["bash"]
