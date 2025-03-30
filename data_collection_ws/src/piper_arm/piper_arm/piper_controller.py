#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
# from sensor_msgs.msg import JointState
from custom_interfaces.msg import JointPosition7

from piper_sdk import C_PiperInterface_V2
from piper_arm.error import CustomErrorMessages
import time
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
        self.piper.MotionCtrl_2(0x01, 0x01, 100, 0xAD)

        self.goto_home()
        self.subscription = self.create_subscription(
            JointPosition7,
            'joint_ctrl_single',
            self.joint_callback,
            10
        )
        self.get_logger().info("✅ Piper Joint Subscriber initialized and ready.")

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
                self.piper.GripperCtrl(abs(position[6]), 1000, 0x01, 0)

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
            self.piper.GripperCtrl(0,1000,0x01, 0)
        start_time = time.time()    
        timeout_sec = 10 
        tolerance = 5000 # 5000 is 5 degrees 

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
                self.piper.GripperCtrl(99200, 1000, 0x01, 0)
            else:
                enable_flag = any(enable_list)
                self.piper.DisableArm(7)
                self.piper.GripperCtrl(99200, 1000, 0x02, 0)

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
