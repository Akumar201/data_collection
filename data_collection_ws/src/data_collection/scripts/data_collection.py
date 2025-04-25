#!/usr/bin/env python3

import os
import subprocess
import time
from datetime import datetime
import rclpy
from rclpy.node import Node


def check_topic_exists(topic_name):
    """
    Check if a topic exists in the ROS2 topic list.
    """
    rclpy.init(args=None)
    node = rclpy.create_node('topic_checker')
    topic_list = node.get_topic_names_and_types()
    node.destroy_node()
    rclpy.shutdown()
    
    for (name, _) in topic_list:
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
        '/camera/right_wrist_cam/color/camera_info',
        '/camera/right_wrist_cam/color/image_rect_raw',
        '/camera/right_wrist_cam/depth/camera_info',
        '/camera/right_wrist_cam/depth/image_rect_raw',
        # Add more topics as needed
    ]

    # List to store missing topics
    missing_topics = []

    # Check which topics exist
    for topic in all_topics:
        if not check_topic_exists(topic):
            missing_topics.append(topic)

    # If there are any missing topics, gracefully exit with a message
    if missing_topics:
        print("The following topics are missing and cannot be recorded:")
        for topic in missing_topics:
            print(f"- {topic}")
        print("Aborting recording due to missing topics.")
        return

    # If all topics are found, proceed with recording
    print(f"Found all {len(all_topics)} topics to record.")

    # Build the ros2 bag record command
    rosbag_cmd = ['ros2', 'bag', 'record', '-o', output_dir, '-s', 'mcap'] + all_topics
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