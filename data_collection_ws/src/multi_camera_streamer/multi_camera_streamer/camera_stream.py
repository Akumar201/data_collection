import cv2
import numpy as np
import pyrealsense2 as rs
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge

class CameraStreamer(Node):
    def __init__(self):
        super().__init__('camera0streamer')
        print("YOLOOOOOOOOOOOOOOOOOOOOO")
        self.bridge = CvBridge()
        # Publisher for the color stream
        self.publisher = self.create_publisher(Image, 'camera/live_video_stream', 10)
        # Timer callback to process frames at ~30Hz
        self.timer = self.create_timer(0.033, self.timer_callback)

        # Set up RealSense pipeline for one camera
        self.pipeline = rs.pipeline()
        self.config = rs.config()
        # If multiple devices are connected, you can specify one using its serial:
        # self.config.enable_device("YOUR_SERIAL_NUMBER")
        self.config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 30)
        try:
            self.pipeline.start(self.config)
            self.get_logger().info("Pipeline started for RealSense camera")
        except Exception as e:
            self.get_logger().error(f"Error starting pipeline: {e}")

    def timer_callback(self):
        try:
            # Wait for a frame set
            frames = self.pipeline.wait_for_frames()
            color_frame = frames.get_color_frame()
            if not color_frame:
                self.get_logger().warning("No color frame received")
                return

            # Convert frame to a NumPy array
            img = np.asanyarray(color_frame.get_data())

            # Convert to ROS Image message and publish
            msg = self.bridge.cv2_to_imgmsg(img, encoding='bgr8')
            self.publisher.publish(msg)

            # Optionally display the image locally for testing
            cv2.imshow("Color Stream", img)
            cv2.waitKey(1)
        except Exception as e:
            self.get_logger().error(f"Error processing frame: {e}")

    def destroy_node(self):
        try:
            self.pipeline.stop()
        except Exception as e:
            self.get_logger().error(f"Error stopping pipeline: {e}")
        super().destroy_node()

def main(args=None):
    rclpy.init(args=args)
    node = CameraStreamer()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        cv2.destroyAllWindows()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
