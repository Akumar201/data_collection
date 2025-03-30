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
        self.piper.MotionCtrl_2(0x01, 0x00, 100, 0x00)

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
        """
        Commands the arm to go to its home position and starts a timer
        to periodically check if the arm has reached home.
        """
        # Command the arm to go home
        self.piper.JointCtrl(0, 0, 0, 0, 0, 0)
        if self.gripper_exist:
            self.piper.GripperCtrl(0, 1000, 0x01, 0)
        
        # Set up parameters for the home check
        self._home_start_time = time.time()
        self._home_timeout_sec = 10
        self._home_tolerance = 5000  # e.g., 5000 corresponds to 5 degrees
        self._home_joint_names = ['joint_1', 'joint_2', 'joint_3',
                                'joint_4', 'joint_5', 'joint_6']
        
        # Create a timer that checks the home position every 0.1 seconds
        self._home_timer = self.create_timer(0.1, self._check_home_position)
        

    def _check_home_position(self):
        """
        Timer callback that checks if the arm has reached its home position.
        Cancels the timer and raises an exception if a timeout occurs.
        """
        elapsed = time.time() - self._home_start_time
        joint_feedback = self.piper.GetArmJointMsgs()
        joints = joint_feedback.joint_state
        # Extract positions from joints using the predefined joint names
        positions = [getattr(joints, name) for name in self._home_joint_names]

        # Check if the arm is within tolerance for all joints
        if all(abs(pos) <= self._home_tolerance for pos in positions):
            self.get_logger().info("✅ Arm reached home position.")
            self._home_timer.cancel()
            return

        # If timeout is reached, log a warning, disable the arm, and raise an error
        if elapsed >= self._home_timeout_sec:
            self.get_logger().warn("⚠️ Timed out waiting for arm to reach home position.")
            error_message = CustomErrorMessages.home_timeout_error(self._home_timeout_sec)
            self.get_logger().warn(error_message)
            self._home_timer.cancel()
            self.enable_piper(enable=False)
            # Raise an exception to trigger graceful shutdown in main()
            raise Exception(error_message)
        else:
            # Log current status (using throttled logging)
            self.get_logger().info(
                f"⏱️ Waiting for home position... Elapsed: {elapsed:.1f}s, Positions: {positions}",
                throttle_duration_sec=5
            )
        
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
