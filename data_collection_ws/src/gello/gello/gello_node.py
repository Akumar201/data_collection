import glob
from dataclasses import dataclass
from typing import Optional, Tuple

import numpy as np
import rclpy
from rclpy.node import Node
# from std_msgs.msg import Float64MultiArray
from sensor_msgs.msg import JointState
from agents.gello_agent import GelloAgent


@dataclass
class Args:
    agent: str = "gello"
    hz: int = 100  # publishing rate in Hz
    start_joints: Optional[Tuple[float, ...]] = None
    gello_port: Optional[str] = None
    verbose: bool = False

class GelloController(Node):
    def __init__(self):
        super().__init__('gello_joint_publisher')

        # Declare and get parameters from ROS 2 launch system
        self.declare_parameter('gello_port', '')
        self.declare_parameter('hz', 200)
        gello_port = self.get_parameter('gello_port').get_parameter_value().string_value
        hz = self.get_parameter('hz').get_parameter_value().integer_value

        if gello_port == "":
            usb_ports = glob.glob("/dev/serial/by-id/usb-FTDI_USB__-__Serial_Converter_*")
            self.get_logger().info(f"Found {len(usb_ports)} ports")
            if usb_ports:
                gello_port = usb_ports[0]
                self.get_logger().info(f"Using port {gello_port}")
            else:
                raise ValueError("No Gello port found.")

        self.agent = GelloAgent(port=gello_port)
        self.publisher_ = self.create_publisher(JointState, 'gello_joint_angles', 10)
        self.timer = self.create_timer(1.0 / hz, self.publish_joint_angles)

    def publish_joint_angles(self):
        joint_angles = self.agent.get_joint_angle()  # Should return a 7-element NumPy array
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = ['joint1', 'joint2', 'joint3', 'joint4', 'joint5', 'joint6', 'gripper']
        msg.position = joint_angles.tolist()
        msg.velocity = [0.0] * 7  
        msg.effort = [0.0] * 7    

        self.publisher_.publish(msg)
        # self.get_logger().info(f'Published: {msg}',  throttle_duration_sec=5.0)

def main():
    rclpy.init()
    node = GelloController()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()
