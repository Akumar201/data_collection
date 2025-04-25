#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from custom_interfaces.msg import JointPosition7
import threading
# import PiperPublisher 
# from piper_arm import PiperPublisher
from geometry_msgs.msg import Pose
from scipy.spatial.transform import Rotation as R
from piper_sdk import C_PiperInterface_V2
from piper_arm.error import CustomErrorMessages
import time
import math
import sys


class PiperController(Node):
    def __init__(self):
        super().__init__('piper_joint_subscriber')
        try:
            self.piper = C_PiperInterface_V2("can0")
            self.piper.ConnectPort()
            self.get_logger().info("✅ Arm Connected Successfully")
        except Exception as e:
            self.get_logger().error(f"❌ Failed to initialize Piper interface: {e}")
            self.get_logger().info("💡 Tip: Use `candump can0` to check CAN communication.")
            rclpy.shutdown()
            sys.exit(1)
            
        self.enable_piper(enable=True)
        self.gripper_val_mutiple = 1
        self.gripper_exist = True
        self.factor = 57324.840764  # ~1000 * 180 / π
        self.piper.MotionCtrl_2(0x01, 0x01, 40, 0xAD)
        self.joint_states = JointState()
        self.joint_states.name = ['joint1', 'joint2', 'joint3', 'joint4', 'joint5', 'joint6', 'gripper']
        self.joint_states.position = [0.0] * 7
        self.joint_states.velocity = [0.0] * 7
        self.joint_states.effort = [0.0] * 7
        

 
        self.joint_pub = self.create_publisher(JointState, 'joint_states_single', 1)
        self.end_pose_pub = self.create_publisher(Pose, 'end_pose', 1)
        
        self.goto_home()
        self.subscription = self.create_subscription(
            JointPosition7,
            'joint_ctrl_single',
            self.joint_callback,
            10
        )
        self.get_logger().info("✅ Piper Joint Subscriber initialized and ready.")

        self.publisher_thread = threading.Thread(target=self.publish_thread)
        self.publisher_thread.start()

    def joint_callback(self, joint_data):
        
        # self.get_logger().info(f"joint data value is {type(joint_data)}",  throttle_duration_sec=5)
        position = [int(val) for val in joint_data.pos]
        
        # Move joints 
        self.piper.JointCtrl(
            position[0],
            position[1],
            position[2],
            position[3],
            position[4],
            position[5]
        )

        # Gripper control
        if self.gripper_exist:
            if len(joint_data.pos) >= 7:
                self.piper.GripperCtrl(abs(position[6]), 5000, 0x01, 0)

        # self.get_logger().info_throttle(5.0, f"Updated joints | Pos: {joint_data.position}")

    def goto_home(self):

        # self.piper.MotionCtrl_2(0x01, 0x01, 50, 0x00)
        self.piper.JointCtrl(
            0,
            0,
            0,
            0,
            0,
            0
        )

        if self.gripper_exist:
            self.piper.GripperCtrl(0,5000,0x01, 0)
        start_time = time.time()    
        timeout_sec = 10 
        tolerance = 5500 # 5000 is 5 degrees 

        joint_names = [
            'joint_1', 'joint_2', 'joint_3',
            'joint_4', 'joint_5', 'joint_6'
        ]

        while (elapsed := time.time() - start_time) < timeout_sec:
            joint_feedback = self.piper.GetArmJointMsgs()
            joints = joint_feedback.joint_state

            # Dynamically extract joint positions using getattr
            positions = [getattr(joints, name) for name in joint_names]

            if all(abs(pos) <= tolerance for pos in positions):
                self.get_logger().info("✅ Arm reached home position.")
                return

            self.get_logger().info(
                f"⏱️ Waiting for home position... Elapsed: {elapsed:.1f}s, Positions: {positions}",
                throttle_duration_sec = 5
            )

            time.sleep(0.1)  # Slight delay to prevent tight polling loop

        self.get_logger().warn("⚠️ Timed out waiting for arm to reach home position.")
        self.enable_piper(enable=False)
        # If we reach here, the arm did not reach home within timeout.
        error_message = CustomErrorMessages.home_timeout_error(timeout_sec)
        self.get_logger().warn(error_message)
        # Raise an exception so that the main loop can handle the shutdown gracefully.
        raise Exception(error_message)
        
    def enable_piper(self, enable: bool):
        '''
        Enable or disable the robotic arm and check the status. 
        Try for 5 seconds. If the operation times out, exit the program.
        '''
        enable_flag = False
        loop_flag = False
        timeout = 5
        start_time = time.time()
        elapsed_time_flag = False
        msg = self.piper.GetArmLowSpdInfoMsgs()

        while not loop_flag:
            elapsed_time = time.time() - start_time
            enable_list = [
                            msg.motor_1.foc_status.driver_enable_status,
                            msg.motor_2.foc_status.driver_enable_status,
                            msg.motor_3.foc_status.driver_enable_status,
                            msg.motor_4.foc_status.driver_enable_status,
                            msg.motor_5.foc_status.driver_enable_status,
                            msg.motor_6.foc_status.driver_enable_status,
                        ]
            if enable:
                enable_flag = all(enable_list)
                self.piper.EnableArm(7)
                self.piper.GripperCtrl(99200, 5000, 0x01, 0)
            else:
                enable_flag = any(enable_list)
                self.piper.DisableArm(7)
                self.piper.GripperCtrl(99200, 5000, 0x02, 0)

            print(f"Enable status: {enable_flag}")

            if enable_flag == enable:
                loop_flag = True
                enable_flag = True
            else:
                loop_flag = False
                enable_flag = False

            # Check if the timeout duration has been exceeded
            if elapsed_time > timeout:
                print(f"Timeout...")
                elapsed_time_flag = True
                enable_flag = False
                loop_flag = True
                break

            time.sleep(0.5)

        resp = enable_flag
        print(f"Returning response: {resp}")
        return resp
    

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


    def publish_thread(self):
        """Publish messages from the robotic arm
        """
        rate = self.create_rate(60)  # 60 Hz
        while rclpy.ok():
            self.publish_joint_states()
            self.publish_end_pose()
            rate.sleep()

def main(args=None):
    rclpy.init(args=args)
    node = None
    try:
        node = PiperController()
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.enable_piper(enable = False)
    except Exception as e:
        if node:
            node.get_logger().error(str(e))
    finally:
        if rclpy.ok() and node is not None:
            node.destroy_node()
            rclpy.shutdown()

if __name__ == '__main__':
    main()
