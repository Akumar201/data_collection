import cv2
import apriltag
import pyrealsense2 as rs
import numpy as np

def detect_apriltags_from_stream():
    # Configure depth and color streams
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

    # Start streaming
    pipeline.start(config)

    try:
        while True:
            # Wait for a coherent pair of frames: depth and color
            frames = pipeline.wait_for_frames()
            color_frame = frames.get_color_frame()
            if not color_frame:
                continue

            # Convert images to numpy arrays
            color_image = np.asanyarray(color_frame.get_data())

            # Convert to grayscale
            gray_image = cv2.cvtColor(color_image, cv2.COLOR_BGR2GRAY)

            # Initialize the AprilTag detector
            options = apriltag.DetectorOptions(families="tag36h11")
            detector = apriltag.Detector(options)
            # Detect AprilTags in the image
            detections = detector.detect(gray_image)
            print("[INFO] {} total AprilTags detected".format(len(detections)))

            # Draw detections on the image
            for detection in detections:
                (ptA, ptB, ptC, ptD) = detection.corners
                ptA = (int(ptA[0]), int(ptA[1]))
                ptB = (int(ptB[0]), int(ptB[1]))
                ptC = (int(ptC[0]), int(ptC[1]))
                ptD = (int(ptD[0]), int(ptD[1]))

                cv2.line(color_image, ptA, ptB, (0, 255, 0), 2)
                cv2.line(color_image, ptB, ptC, (0, 255, 0), 2)
                cv2.line(color_image, ptC, ptD, (0, 255, 0), 2)
                cv2.line(color_image, ptD, ptA, (0, 255, 0), 2)

                (cX, cY) = (int(detection.center[0]), int(detection.center[1]))
                cv2.circle(color_image, (cX, cY), 5, (0, 0, 255), -1)

                tag_id = detection.tag_id
                cv2.putText(color_image, str(tag_id), (ptA[0], ptA[1] - 15),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # Display the image
            cv2.imshow("AprilTag Detection", color_image)

            # Break the loop on 'q' key press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        # Stop streaming
        pipeline.stop()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    detect_apriltags_from_stream()

def detect_apriltags(image_path):
    # Load the image
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        print("Error: Unable to load image.")
        return

    # Initialize the AprilTag detector
    detector = apriltag.Detector()

    # Detect AprilTags in the image
    detections = detector.detect(image)

    # Draw detections on the image
    for detection in detections:
        (ptA, ptB, ptC, ptD) = detection.corners
        ptA = (int(ptA[0]), int(ptA[1]))
        ptB = (int(ptB[0]), int(ptB[1]))
        ptC = (int(ptC[0]), int(ptC[1]))
        ptD = (int(ptD[0]), int(ptD[1]))

        cv2.line(image, ptA, ptB, (0, 255, 0), 2)
        cv2.line(image, ptB, ptC, (0, 255, 0), 2)
        cv2.line(image, ptC, ptD, (0, 255, 0), 2)
        cv2.line(image, ptD, ptA, (0, 255, 0), 2)

        (cX, cY) = (int(detection.center[0]), int(detection.center[1]))
        cv2.circle(image, (cX, cY), 5, (0, 0, 255), -1)

        tag_id = detection.tag_id
        cv2.putText(image, str(tag_id), (ptA[0], ptA[1] - 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Display the image
    cv2.imshow("AprilTag Detection", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    image_path = "path_to_your_image.jpg"
    detect_apriltags(image_path)