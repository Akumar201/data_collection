#!/usr/bin/env python3

import os
import subprocess
import time
from datetime import datetime

import rclpy
from rclpy.node import Node
from rclpy.topic_or_service_is_hidden import topic_or_service_is_hidden


def check_topic_exists(topic_name):
    """
    Check if a topic exists in the ROS2 topic list.
    """
    rclpy.init(args=None)
    node = rclpy.create_node('topic_checker')
    topic_list = node.get_topic_names_and_types()
    node.destroy_node()
    rclpy.shutdown()
    # print(topic_list)
    for (name, _) in topic_list:
        print("topic available",name)
        print("topic_name",topic_name)
        if name == topic_name:
            return True
    return False


def record_rosbag():
    """Start recording topics using ros2 bag record in mcap format."""
    output_dir = "rosbag_data"  # Fixed folder name for all recordings

    # Remove the existing folder if it exists
    if os.path.exists(output_dir):
        import shutil
        shutil.rmtree(output_dir)

    # Define the topics to record
    all_topics = [
        # '/right_wrist_cam/color/image_rect_raw',
        # '/right_wrist_cam/aligned_depth_to_color/image_raw',
        # '/right_wrist_cam/aligned_depth_to_color/camera_info',
        # '/high_cam/color/image_rect_raw',
        # '/high_cam/aligned_depth_to_color/image_raw',
        # '/high_cam/aligned_depth_to_color/camera_info'
        '/camera/right_wrist_cam/color/camera_info',
        '/camera/right_wrist_cam/color/image_rect_raw',
        '/camera/right_wrist_cam/color/metadata',
        '/camera/right_wrist_cam/depth/camera_info',
        '/camera/right_wrist_cam/depth/image_rect_raw',
        '/camera/right_wrist_cam/depth/metadata',
        '/camera/right_wrist_cam/extrinsics/depth_to_color',
        '/camera/right_wrist_cam/extrinsics/depth_to_infra1'
    ]

    # Check available topics
    valid_topics = [topic for topic in all_topics if check_topic_exists(topic)]

    if not valid_topics or len(valid_topics) < len(all_topics):
        print("Relevant topics not found. Aborting recording.")
        return

    print(f"Found {len(valid_topics)} valid topics to record.")

    # Build the ros2 bag record command
    rosbag_cmd = ['ros2', 'bag', 'record', '-o', output_dir, '-s', 'mcap'] + valid_topics
    print("Running command:", " ".join(rosbag_cmd))

    # Start the rosbag recording process
    process = subprocess.Popen(rosbag_cmd)

    try:
        print("Recording... Press Ctrl+C to stop.")
        process.wait()
    except KeyboardInterrupt:
        print("Stopping recording...")
        process.terminate()

    print("Data collection stopped.")


if __name__ == "__main__":
    record_rosbag()
