import pyrealsense2 as rs
import numpy as np
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst

Gst.init(None)

# GStreamer pipeline
pipeline_str = (
    'appsrc name=source is-live=true block=true format=TIME do-timestamp=true ! '
    'videoconvert ! '
    'x264enc tune=zerolatency bitrate=3000 speed-preset=superfast key-int-max=10 ! '
    'rtph264pay config-interval=1 pt=96 ! '
    'udpsink host=192.168.50.27 port=5000'
)
pipeline = Gst.parse_launch(pipeline_str)
appsrc = pipeline.get_by_name('source')

# Set video format (RealSense gives BGR)
caps = Gst.Caps.from_string("video/x-raw,format=BGR,width=640,height=480,framerate=30/1")
appsrc.set_property("caps", caps)

# Start pipeline
pipeline.set_state(Gst.State.PLAYING)

# RealSense config
rs_pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
rs_pipeline.start(config)

frame_count = 0
duration = Gst.util_uint64_scale_int(1, Gst.SECOND, 30)

try:
    while True:
        frames = rs_pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()
        if not color_frame:
            continue

        frame = np.asanyarray(color_frame.get_data())
        data = frame.tobytes()

        buf = Gst.Buffer.new_allocate(None, len(data), None)
        buf.fill(0, data)
        buf.duration = duration
        buf.pts = buf.dts = frame_count * duration
        frame_count += 1

        # print("Timestamp:", color_frame.get_timestamp())

        retval = appsrc.emit("push-buffer", buf)
        if retval != Gst.FlowReturn.OK:
            print("Failed to push buffer:", retval)
            break


except KeyboardInterrupt:
    print("Interrupted.")

finally:
    rs_pipeline.stop()
    pipeline.set_state(Gst.State.NULL)
