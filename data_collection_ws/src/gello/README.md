# Gello ROS 2 Controller

This module provides an interface for **Gello**, a 6-DoF joystick-style input device for controlling a robotic arm.  
It is **independent of the robotic arm itself** — it only publishes `JointState` messages, which can be consumed by any compatible robot.

---

## 📡 Topics

The joint angles are published on the following ROS 2 topics:

- `master/gello_left`
- `master/gello_right`

---

## 🚀 Launching Gello Controller

### 🦾 Single Arm (Default: Left)

To launch a **single Gello device** (for controlling one arm), run:

```bash
ros2 launch gello gello_single_node.launch.py
```

NOTE: This defaults to the left arm. You can change the port or remap topics in the launch file if needed.


## 🤖 Bimanual Mode (Left & Right Arms)

To launch two Gello devices simultaneously for bimanual control, run:

```bash
ros2 launch gello gello_double_node.launch.py
```

This will start two Gello controllers — one for each arm.

## ⚙️ Calibrating a New Gello Device

When installing a new Gello, you must run a one-time calibration script to determine joint encoder offsets.

We’ve included a simple script that helps compute these offsets automatically.
🧭 Steps
1. Set your Gello into a known configuration (e.g. all joints at 0, 0, 0, 0, 0, 0 radians)
2. Run the calibration script:
```bash
python scripts/gello_get_offset.py \
    --start-joints 0 0 0 0 0 0 \  # in radians
    --joint-signs 1 1 1 1 1 1 \
    --port /dev/serial/by-id/usb-FTDI_USB__-__Serial_Converter_FT7WBG6
```

## 🔧 Arguments

--start-joints: Your known Gello joint angles (in radians)
--joint-signs: Direction multipliers for each joint (see below)
--port: Serial port of your Gello device

To find your serial port:

On Ubuntu:

    ls /dev/serial/by-id/

Look for something like:
```bash
usb-FTDI_USB__-__Serial_Converter_*
```
On macOS:
Look in /dev/ for something like:

    cu.usbserial*

🔁 Joint Signs

These values correct the direction of motion for each joint.

AgileX configuration:
```bash
1 1 -1 1 1 1
```
