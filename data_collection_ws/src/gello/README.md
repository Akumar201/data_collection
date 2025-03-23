This module is for controlling gello to control robotic arm, it is independent of robotic arm. 
The topic on which the joint angles are published are master/gello_left  and master/gello_right

To launch the node you can simply use the following command ros2 launch gello gello_single_node.launch.py for launching single gello to control single arm , right now the default is left arm. You can use ros2 launch gello gello_double_node.launch.py to launch bimanual arm. 


When installing new gello you need to run the gello_get_offset.py to get the offset and edit the gello_agent.py accordingly. 


We have created a simple script to automatically detect the joint offset:

    set GELLO into a known configuration, where you know what the corresponding joint angles should be. For example, we set out GELLO in this configuration, where we know the desired ground truth joints. (0, 0, 0, 0, 0, 0)

    run

python scripts/gello_get_offset.py \
    --start-joints 0 0 0 0 0 0 \ # in radians
    --joint-signs 1 1 -1 1 1 1 \
    --port /dev/serial/by-id/usb-FTDI_USB__-__Serial_Converter_FT7WBG6
# replace values with your own

    Use the known starting joints for start-joints.
    Use the joint-signs for your own robot (see below).
    Use your serial port for port. You can find the port id of your U2D2 Dynamixel device by running ls /dev/serial/by-id and looking for the path that starts with usb-FTDI_USB__-__Serial_Converter (on Ubuntu). On Mac, look in /dev/ and the device that starts with cu.usbserial

joint-signs
AgileX 1 1 -1 1 1 1