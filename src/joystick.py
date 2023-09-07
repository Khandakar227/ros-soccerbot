# !/usr/bin/python3
import rospy
import bluetooth
import threading
import math
import time
from sensor_msgs.msg import Joy

NODE_NAME = "soccerbot_bluetooth"
# bt_addr = "00:22:06:01:29:0C"     #HC-05
bt_addr = "00:18:E4:40:00:06"       #HC-06
port = 1

BT_DATA = bytearray([0, 0, 0, 0, 0, 0, 0, 0, 0, 60]) # 60 == '>' which is used as an END DELIMITER
socket:bluetooth.BluetoothSocket


# Bluetooth related functions
def get_nearby_devices():
    nearby_devices = bluetooth.discover_devices()
    for i in nearby_devices:
        print(f"{bluetooth.lookup_name(i)} - {i}")


def connect():
    global socket
    # Create a bluetooth socket
    socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    # connect to your module on a specified port
    socket.connect((bt_addr, port))


def init_transmission():
    global socket
    try:
        print("Connecting to device " + bt_addr+ "...")
        connect()
        print("Connected")
        while True:
            socket.send(bytes(BT_DATA))
            time.sleep(0.15)
    except Exception as e:
        print(e)
        time.sleep(3)
        socket.close()
        init_transmission()


def get_joystick_thumb(_x, _y, threshold = 255):
    x = int(_x*threshold)
    y = int(_y*threshold)
    r = int(((x*x + y*y)**0.5))
    r = r if r <= 255 else 255
    r = 0 if r <= 5 else r

    theta = int(math.degrees(math.atan2(_y, -_x)))
    theta = (theta if theta >= 0 else 360 + theta)*240//360
    if theta == 0 and r > 0: theta += 1
    return (r, theta) 


def gamepad_callback(data:Joy):
    global BT_DATA
    lr, ltheta = get_joystick_thumb(data.axes[0], data.axes[1])
    rr, rtheta = get_joystick_thumb(data.axes[2], data.axes[3])

    BT_DATA[5], BT_DATA[6], BT_DATA[7], BT_DATA[8] = rr, rtheta, lr, ltheta  

    rospy.loginfo(f"{lr}, {ltheta}, {rr}, {rtheta}")
    # rospy.loginfo(data)



if __name__ == '__main__':
    rospy.init_node(NODE_NAME)
    rospy.Subscriber("joy", Joy, gamepad_callback)
    bt_thread = threading.Thread(target=init_transmission, daemon=True)
    bt_thread.start()
    rospy.spin()