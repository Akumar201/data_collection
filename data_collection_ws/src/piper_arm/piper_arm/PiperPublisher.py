import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from geometry_msgs.msg import Pose
from piper_sdk import C_PiperInterface
from scipy.spatial.transform import Rotation as R
import threading
import math
import time


class PiperPublisher(Node):
    """Class for publishing joint states and end effector pose."""

    def __init__(self, can_port='can0'):
        super().__init__('arm_publisher')
        self.declare_parameter('can_port', can_port)
        self.can_port = self.get_parameter('can_port').get_parameter_value().string_value

        self.joint_pub = self.create_publisher(JointState, 'joint_states', 1)
        self.end_pose_pub = self.create_publisher(Pose, 'end_pose', 1)

        self.piper = C_PiperInterface(can_name=self.can_port)
        self.piper.ConnectPort()

        self.joint_states = JointState()
        self.joint_states.name = ['joint1', 'joint2', 'joint3', 'joint4', 'joint5', 'joint6', 'gripper']
        self.joint_states.position = [0.0] * 7
        self.joint_states.velocity = [0.0] * 7
        self.joint_states.effort = [0.0] * 7

    def publish_joint_states(self):
        """Publish the current joint states."""
        joint_0 = (self.piper.GetArmJointMsgs().joint_state.joint_1 / 1000) * 0.017444  # Convert from encoder units to radians
        joint_1 = (self.piper.GetArmJointMsgs().joint_state.joint_2 / 1000) * 0.017444
        joint_2 = (self.piper.GetArmJointMsgs().joint_state.joint_3 / 1000) * 0.017444
        joint_3 = (self.piper.GetArmJointMsgs().joint_state.joint_4 / 1000) * 0.017444
        joint_4 = (self.piper.GetArmJointMsgs().joint_state.joint_5 / 1000) * 0.017444
        joint_5 = (self.piper.GetArmJointMsgs().joint_state.joint_6 / 1000) * 0.017444
        joint_6 = self.piper.GetArmGripperMsgs().gripper_state.grippers_angle / 1000000  # Gripper angle

        self.joint_states.position = [joint_0, joint_1, joint_2, joint_3, joint_4, joint_5, joint_6]
        self.joint_states.header.stamp = self.get_clock().now().to_msg()

        self.joint_pub.publish(self.joint_states)

    def publish_end_pose(self):
        """Publish the end effector pose (position and orientation)."""
        end_pose = Pose()
        end_pose.position.x = self.piper.GetArmEndPoseMsgs().end_pose.X_axis / 1000000
        end_pose.position.y = self.piper.GetArmEndPoseMsgs().end_pose.Y_axis / 1000000
        end_pose.position.z = self.piper.GetArmEndPoseMsgs().end_pose.Z_axis / 1000000

        roll = self.piper.GetArmEndPoseMsgs().end_pose.RX_axis / 1000
        pitch = self.piper.GetArmEndPoseMsgs().end_pose.RY_axis / 1000
        yaw = self.piper.GetArmEndPoseMsgs().end_pose.RZ_axis / 1000

        # Convert Euler angles to quaternion for orientation
        roll = math.radians(roll)
        pitch = math.radians(pitch)
        yaw = math.radians(yaw)
        quaternion = R.from_euler('xyz', [roll, pitch, yaw]).as_quat()

        end_pose.orientation.x = quaternion[0]
        end_pose.orientation.y = quaternion[1]
        end_pose.orientation.z = quaternion[2]
        end_pose.orientation.w = quaternion[3]

        self.end_pose_pub.publish(end_pose)

    def start_publishing(self):
        """Start publishing joint data and end pose in a separate thread."""
        def publish_thread():
            rate = self.create_rate(60)  # 60 Hz
            while rclpy.ok():
                self.publish_joint_states()
                self.publish_end_pose()
                rate.sleep()

        publisher_thread = threading.Thread(target=publish_thread)
        publisher_thread.daemon = True  # Allow thread to exit when the main program exits
        publisher_thread.start()


def main(args=None):
    rclpy.init(args=args)
    arm_publisher = PiperPublisher()

    arm_publisher.start_publishing()  # Start the publishing thread

    try:
        rclpy.spin(arm_publisher)
    except KeyboardInterrupt:
        pass
    finally:
        arm_publisher.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()