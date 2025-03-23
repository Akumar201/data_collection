from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument, GroupAction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import PushRosNamespace
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
    # Declare common arguments (you can override per arm if needed)
    can_port_left_arg = DeclareLaunchArgument(
        'can_left',
        default_value='can0',
        description='CAN port for the left arm'
    )

    can_port_right_arg = DeclareLaunchArgument(
        'can_right',
        default_value='can1',
        description='CAN port for the right arm'
    )

    auto_enable_arg = DeclareLaunchArgument(
        'auto_enable',
        default_value='true',
        description='Auto-enable Piper arm'
    )

    gripper_exist_arg = DeclareLaunchArgument(
        'gripper_exist',
        default_value='true',
        description='Gripper attached'
    )

    gripper_val_mutiple_arg = DeclareLaunchArgument(
        'gripper_val_mutiple',
        default_value='1',
        description='Gripper scaling multiplier'
    )

    # Left arm node
    left_arm = GroupAction([
        PushRosNamespace('left'),
        Node(
            package='piper_arm',
            executable='piper_controller',
            name='piper_controller_left',
            output='screen',
            parameters=[{
                'can_port': LaunchConfiguration('can_port_left'),
                'auto_enable': LaunchConfiguration('auto_enable'),
                'gripper_exist': LaunchConfiguration('gripper_exist'),
                'gripper_val_mutiple': LaunchConfiguration('gripper_val_mutiple')
            }],
            remappings=[
                ('joint_ctrl_single', 'master/gello_left'),
            ]
        )
    ])

    # Right arm node
    right_arm = GroupAction([
        PushRosNamespace('right'),
        Node(
            package='piper_arm',
            executable='piper_controller',
            name='piper_controller_right',
            output='screen',
            parameters=[{
                'can_port': LaunchConfiguration('can_port_right'),
                'auto_enable': LaunchConfiguration('auto_enable'),
                'gripper_exist': LaunchConfiguration('gripper_exist'),
                'gripper_val_mutiple': LaunchConfiguration('gripper_val_mutiple')
            }],
            remappings=[
                ('joint_ctrl_single', 'master/gello_right'),
            ]
        )
    ])

    return LaunchDescription([
        can_port_left_arg,
        can_port_right_arg,
        auto_enable_arg,
        gripper_exist_arg,
        gripper_val_mutiple_arg,
        left_arm,
        right_arm
    ])
