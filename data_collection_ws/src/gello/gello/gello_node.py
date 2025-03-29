import glob
import sys
import argparse
import numpy as np

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from agents.gello_agent import GelloAgent


class GelloController(Node):
    def __init__(self):
        super().__init__('gello_joint_publisher')

        self.declare_parameter('gello_port', '')
        self.declare_parameter('hz', 100)
        self.declare_parameter('dev_mode', False) 

        # Reading Parameters
        self.dev_mode = self.get_parameter('dev_mode').get_parameter_value().bool_value
        self.gello_port = self.get_parameter('gello_port').get_parameter_value().string_value
        self.hz = self.get_parameter('hz').get_parameter_value().integer_value


        self.scale_factor_piper = 57324.84
        self.scale_factor_gripper_piper = 90000
        self.joint_limits_piper = {
            'joint1': [-2.6170, 2.6170],
            'joint2': [0, 3.14],
            'joint3': [-2.967, 0],
            'joint4': [-1.745, 1.745],
            'joint5': [-1.22, 1.22],
            'joint6': [-2.0922, 2.0922]
        }
        self.joint_names = list(self.joint_limits_piper.keys()) + ['joint7']

        self.msg = JointState()
        self.msg.name = self.joint_names
        self.msg.velocity = [0.0] * 7
        self.msg.effort = [0.0] * 7
        self.msg.position = [0.0] * 7

        # Precompute min and max limit arrays for efficient clipping
        self.min_limits = np.array([self.joint_limits_piper[j][0] for j in self.joint_names[:6]])
        self.max_limits = np.array([self.joint_limits_piper[j][1] for j in self.joint_names[:6]])

        self.connect_gello(self.gello_port)

        self.publisher_ = self.create_publisher(JointState, 'gello_joint_angles', 10)
        self.timer = self.create_timer(1.0 / self.hz, self.publish_joint_angles)


    def connect_gello(self, gello_port: str):
        """
        Connects to Gello hardware by using provided port or auto-detecting it.
        """
        if not gello_port:
            usb_ports = glob.glob("/dev/serial/by-id/usb-FTDI_USB__-__Serial_Converter_*")
            if not usb_ports:
                raise RuntimeError("❌ No Gello port found!")
            gello_port = usb_ports[0]
            self.get_logger().info(f"✅ Auto-detected Gello port: {gello_port}")
        else:
            self.get_logger().info(f"🔌 Using provided Gello port: {gello_port}")

        self.agent = GelloAgent(port=gello_port)

    def publish_joint_angles(self):
        
        try:
            joint_angles = self.agent.get_joint_angle()
        except Exception as e:
            self.get_logger().error(f"Failed to read joint angles: {e}")
            return

        scaled_joined_anlges = self.clip_and_scale(joint_angles)
        
        self.msg.header.stamp = self.get_clock().now().to_msg()
        self.msg.position = scaled_joined_anlges.tolist()
        self.publisher_.publish(self.msg)
        
    def clip_and_scale(self, joint_angles: np.ndarray) -> np.ndarray:
        # Clip first 6 joints
        clipped = np.clip(joint_angles[:6], self.min_limits, self.max_limits)
        gripper = joint_angles[6]

        if self.dev_mode:
            # In dev mode, return raw values (just clipped)
            return np.append(clipped, gripper)

        # Scale arm joints and gripper
        scaled = np.round(clipped * self.scale_factor_piper).astype(np.int32)
        gripper_scaled = int(gripper * self.scale_factor_gripper_piper)

        # Convert result to float64 to satisfy ROS 2 type constraints
        result = np.append(scaled, gripper_scaled)
        return result.astype(np.float64)

def main():
    rclpy.init()
    node = GelloController()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Exception during node startup: {e}")
    finally:
        if rclpy.ok() :
            node.destroy_node()
            rclpy.shutdown()


if __name__ == "__main__":
    main()
