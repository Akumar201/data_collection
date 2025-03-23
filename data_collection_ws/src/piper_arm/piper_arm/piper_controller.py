#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from piper_sdk import C_PiperInterface_V2
import math
import time
import sys

def clip(value, min_val, max_val):
    return max(min(value, max_val), min_val)

class PiperController(Node):
    def __init__(self):
        super().__init__('piper_joint_subscriber')
        self.piper = C_PiperInterface_V2("can0")
        self.piper.ConnectPort()
        # self.piper.EnableArm(7)
        enable_piper(piper=self.piper)
        self.gripper_val_mutiple = 1
        self.gripper_exist = True
        self.factor = 57324.840764  # ~1000 * 180 / π

        self.goto_home()
        self.piper.MotionCtrl_2(0x01, 0x01, 100, 0xAD)
        self.subscription = self.create_subscription(
            JointState,
            'joint_ctrl_single',
            self.joint_callback,
            10
        )

        self.get_logger().info("Piper Joint Subscriber initialized and ready.")

    def joint_callback(self, joint_data):
        joint_positions = {}
        joint_6 = 0

        self.get_logger().info(f"Received Joint States: {joint_data}" , throttle_duration_sec = 5)
        # Position conversion
        for idx, joint_name in enumerate(joint_data.name):
            if idx < 6:
                joint_positions[joint_name] = round(joint_data.position[idx] * self.factor)

        # Gripper position
        if len(joint_data.position) >= 7:
            joint_6 = round(joint_data.position[6] * 1000000)
            joint_6 *= self.gripper_val_mutiple

        # Move joints
        self.piper.JointCtrl(
            joint_positions.get('joint1'),
            joint_positions.get('joint2'),
            joint_positions.get('joint3'),
            joint_positions.get('joint4'),
            joint_positions.get('joint5'),
            joint_positions.get('joint6')
        )

        # Gripper control
        if self.gripper_exist:
            if len(joint_data.effort) >= 7:
                effort = clip(joint_data.effort[6], 0.5, 3)
                effort_val = round(effort * 1000) if not math.isnan(effort) else 1000
            else:
                effort_val = 1000
            self.piper.GripperCtrl(abs(joint_6), effort_val, 0x01, 0)

        # self.get_logger().info_throttle(5.0, f"Updated joints | Pos: {joint_data.position}")

    def goto_home(self):

        self.piper.MotionCtrl_2(0x01, 0x01, 50, 0x00)
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
        tolerance = 10

       
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
        rclpy.shutdown()
        sys.exit(1)
        


def enable_piper(piper:C_PiperInterface_V2):
    '''
    使能机械臂并检测使能状态,尝试5s,如果使能超时则退出程序
    '''
    enable_flag = False
    # 设置超时时间（秒）
    timeout = 5
    # 记录进入循环前的时间
    start_time = time.time()
    elapsed_time_flag = False
    while not (enable_flag):
        elapsed_time = time.time() - start_time
        print("--------------------")
        enable_flag = piper.GetArmLowSpdInfoMsgs().motor_1.foc_status.driver_enable_status and \
            piper.GetArmLowSpdInfoMsgs().motor_2.foc_status.driver_enable_status and \
            piper.GetArmLowSpdInfoMsgs().motor_3.foc_status.driver_enable_status and \
            piper.GetArmLowSpdInfoMsgs().motor_4.foc_status.driver_enable_status and \
            piper.GetArmLowSpdInfoMsgs().motor_5.foc_status.driver_enable_status and \
            piper.GetArmLowSpdInfoMsgs().motor_6.foc_status.driver_enable_status
        print("使能状态:",enable_flag)
        piper.EnableArm(7)
        piper.GripperCtrl(0,1000,0x01, 0)
        print("--------------------")
        # 检查是否超过超时时间
        if elapsed_time > timeout:
            print("超时....")
            elapsed_time_flag = True
            enable_flag = True
            break
        time.sleep(1)
        pass
    if(elapsed_time_flag):
        print("程序自动使能超时,退出程序")
        exit(0)


def main(args=None):
    rclpy.init(args=args)
    node = PiperController()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
