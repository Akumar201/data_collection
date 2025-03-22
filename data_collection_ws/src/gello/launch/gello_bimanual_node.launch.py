from launch import LaunchDescription
from launch_ros.actions import Node
import os
import yaml

CONFIG_FILE_PATH = "/app/config/config.local.yaml"


def load_serials():
    """Load the serial numbers for cameras and gello arms from the YAML config file."""
    if not os.path.exists(CONFIG_FILE_PATH):
        raise FileNotFoundError(f"Config file not found: {CONFIG_FILE_PATH}")
    
    with open(CONFIG_FILE_PATH, 'r') as file:
        config = yaml.safe_load(file)

    station_cfg = config.get('station', {})
    gello_serial = station_cfg.get('gello', {})

    serials = {
        'left_gello': gello_serial.get('left_gello_serial_no', ''),
        'right_gello': gello_serial.get('right_gello_serial_no', ''),
    }

    for name, val in serials.items():
        if not val:
            raise ValueError(f"Missing value for '{name}' in the config file.")
    
    return serials


def generate_launch_description():

    serials = load_serials()
    left_gello_port = serials['left_gello']
    right_gello_port = serials['right_gello']

    return LaunchDescription([

        # Left arm node
        Node(
            package='gello',
            executable='gello_node',
            name='gello_node_left',
            namespace='left',
            output='screen',
            parameters=[
                {'gello_port': left_gello_port},
                {'hz': 100}
            ],
            remappings=[
                ('gello_joint_angles', 'master/left_gello')
            ]
        ),

        # Right arm node
        Node(
            package='gello',
            executable='gello_node',
            name='gello_node_right',
            namespace='right',
            output='screen',
            parameters=[
                {'gello_port': right_gello_port},
                {'hz': 100}
            ],
            remappings=[
                ('gello_joint_angles', 'master/right_gello')
            ]
        )
    ])
