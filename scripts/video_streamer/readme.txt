------
On the reciever side, run the following

gst-launch-1.0 udpsrc port=5000 caps="application/x-rtp, media=video, clock-rate=90000, encoding-name=H264, payload=96" \
! rtph264depay ! avdec_h264 ! autovideosink sync=false

-------

ON the sender side ( to hwere camera is connected)

python3 send_video_stream.py
