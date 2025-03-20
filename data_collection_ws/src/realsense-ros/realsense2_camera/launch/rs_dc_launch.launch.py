import os
import yaml
import launch
import launch_ros.actions
from launch.actions import OpaqueFunction

# Set the path to the config file (update this if needed)
CONFIG_FILE_PATH = "/app/config/config.local.yaml"

def load_serial_numbers():
    """Load the serial numbers for all cameras from the YAML config file."""
    if not os.path.exists(CONFIG_FILE_PATH):
        raise FileNotFoundError(f"Config file not found: {CONFIG_FILE_PATH}")
    
    with open(CONFIG_FILE_PATH, 'r') as file:
        config = yaml.safe_load(file)

    cameras = config.get('station', {}).get('cameras', {})
    serial_numbers = {
        'left_wrist_cam': cameras.get('left_wrist', {}).get('serial_no', ''),
        'right_wrist_cam': cameras.get('right_wrist', {}).get('serial_no', ''),
        'high_cam': cameras.get('high', {}).get('serial_no', '')
    }
    
    for cam_name, serial_no in serial_numbers.items():
        if not serial_no:
            raise ValueError(f"No serial number found for '{cam_name}' in the config file.")
    
    return serial_numbers

def launch_setup(context, *args, **kwargs):
    """Dynamically set the RealSense serial numbers for all cameras."""
    serial_numbers = load_serial_numbers()
    
    nodes = []
    for cam_name, serial_no in serial_numbers.items():
        nodes.append(
            launch_ros.actions.Node(
                package='realsense2_camera',
                executable='realsense2_camera_node',
                name=cam_name,
                parameters=[{
                    'serial_no': serial_no,
                    'enable_depth': True,
                    'enable_color': True,
                    'align_depth': True,
                    'enable_pointcloud': True,
                }],
                output='screen'
            )
        )
    return nodes

def generate_launch_description():
    return launch.LaunchDescription([
        OpaqueFunction(function=launch_setup)
    ])
