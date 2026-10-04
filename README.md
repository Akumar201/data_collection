# Data Collection Project

This project contains code for **data collection**.
## 🐳  Running the Docker
Works on both x86 (amd64) and ARM (arm64, e.g. Orange Pi) hosts with Docker Compose v2 or v1.
The scripts can be run from any directory:

```
./scripts/up_data_collection.sh       # (optionally rebuild), start and attach to the container
./scripts/build_data_collection.sh    # only build the image
./scripts/start_data_collection.sh    # only start the container in the background
```

The NVIDIA GPU override (`docker_env/docker-compose.nvidia.yml`) is added automatically on hosts with the NVIDIA runtime.

## 📁 Project Structure

### **1️⃣ `config/`**
This folder contains configuration files, including [`config.yaml`](https://github.com/Akumar201/data_collection_ws/blob/master/config/config.yaml).

**Setup Instructions:**
- When cloning this repository, **DO NOT edit `config.yaml` directly**.
- Instead, create a **`config.local.yaml`** file:
  ```sh
  cp config/config.yaml config/config.local.yaml
Edit config.local.yaml to match your station-specific settings, such as:
- Camera serial numbers
- Station name
- Any other necessary configurations.

### **1️⃣ `data_collection_ws/`**
This folder contains the ROS2 workspace for data collection.


### **3️⃣ `docker_env/`**
This folder includes Docker-related files, such as:

    docker-compose.yml
    Dockerfile
    Other Docker configurations.

### **4️⃣ `scripts/`**
This folder contains useful bash scripts for automation and setup.


## 🚀 Running the Camera Node

Follow these steps to launch the camera node:

### 1️⃣ Build the ROS2 workspace using colcon:

    cd data_collection_ws
    colcon build

### 2️⃣ Source the workspace:

    source install/setup.bash

### 3️⃣ Launch the camera node:

    ros2 launch realsense2_camera rs_dc_launch.launch.py

### 4️⃣ View the image stream using rqt_image_view:

    ros2 run rqt_image_view rqt_image_view

