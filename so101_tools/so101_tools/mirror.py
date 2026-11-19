#!/usr/bin/env python3
import math
import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from sensor_msgs.msg import JointState

from scservo_sdk import (
    PortHandler,
    PacketHandler,
    GroupSyncRead,
    SCS_LOWORD,
    SCS_HIWORD,
    SCS_TOHOST,
    COMM_SUCCESS
)

# Control table address
ADDR_STS_PRESENT_POSITION  = 56

# STS3215 Servo Parameters
TICKS_PER_REV = 4096
CENTER_TICK = 2047

# Default setting
SCS_IDS = [1, 2, 3, 4, 5, 6]  # SCServo#1 IDs
SCS_JOINT_NAMES = ['shoulder_pan', 'shoulder_lift', 'elbow_flex', 'wrist_flex', 'wrist_roll', 'gripper']
BAUDRATE = 1000000           # SCServo default baudrate : 1000000
DEVICENAME = '/dev/ttyACM0'    # Check which port is being used on your controller

protocol_end = 0                 # SCServo bit end(STS/SMS=0, SCS=1)


class Mirror(Node):
    def __init__(self):
        super().__init__('mirror')

        self.publisher_ = self.create_publisher(JointState, '/joint_states', 10)
        self.init_servo_comms()
        
        timer_period = 1 / 30  # 30Hz
        self.timer = self.create_timer(timer_period, self.timer_callback)

    def timer_callback(self):
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = list(SCS_JOINT_NAMES)
        msg.position = [0] * 6
        msg.velocity = [0] * 6
        msg.effort = [0] * 6


        # Syncread present position
        scs_comm_result = self.groupSyncRead.txRxPacket()
        if scs_comm_result != COMM_SUCCESS:
            self.get_logger().error("%s" % self.packetHandler.getTxRxResult(scs_comm_result))
            return

        for sid in SCS_IDS:
            # Check if groupsyncread data of SCServo#i is available
            scs_getdata_result = self.groupSyncRead.isAvailable(sid, ADDR_STS_PRESENT_POSITION, 4)
            scs_present_position_speed = 0
            if scs_getdata_result == True:
                # Get SCServo#sid present position value
                scs_present_position_speed = self.groupSyncRead.getData(sid, ADDR_STS_PRESENT_POSITION, 4)
            else:
                self.get_logger().error("[ID:%03d] groupSyncRead getdata failed" % sid)
                return

            scs_present_position = SCS_LOWORD(scs_present_position_speed)
            scs_present_speed = SCS_HIWORD(scs_present_position_speed)

            scs_present_position_rad = ((scs_present_position - CENTER_TICK) / TICKS_PER_REV) * (2 * math.pi)
            scs_present_speed_rad_s = (SCS_TOHOST(scs_present_speed, 15) / TICKS_PER_REV) * (2 * math.pi)

            # self.get_logger().info("Position [ID:%03d] PresPosTicks:%03d PresPosRad:%05f" % (sid, scs_present_position, scs_present_position_rad))
            # self.get_logger().info("Velocity [ID:%03d] PresSpeedTicks:%03d PresSpeedRad:%05f" % (sid, SCS_TOHOST(scs_present_speed, 15), scs_present_speed_rad_s))

            msg.position[sid - 1] = scs_present_position_rad
            msg.velocity[sid - 1] = scs_present_speed_rad_s


        self.publisher_.publish(msg)

    def init_servo_comms(self):
        # Initialize PortHandler instance
        # Set the port path
        # Get methods and members of PortHandlerLinux
        self.portHandler = PortHandler(DEVICENAME)

        # Initialize PacketHandler instance
        # Get methods and members of Protocol
        self.packetHandler = PacketHandler(protocol_end)

        # Initialize GroupSyncRead instace for Present Position
        self.groupSyncRead = GroupSyncRead(self.portHandler, self.packetHandler, ADDR_STS_PRESENT_POSITION, 4)

        # Open port
        if not self.portHandler.openPort():
            raise RuntimeError("Failed to open the port")
        else:
            self.get_logger().info("Succeeded to open the port")

        if not self.portHandler.setBaudRate(BAUDRATE):
            raise RuntimeError("Failed to change the baudrate")
        else:
            self.get_logger().info("Succeeded to change the baudrate")

        for sid in SCS_IDS:
            # Add parameter storage for SCServo#i present position value
            scs_addparam_result = self.groupSyncRead.addParam(sid)
            self.get_logger().info("[ID:%03d] groupSyncRead addparam result: %s" % (sid, scs_addparam_result))
            if scs_addparam_result != True:
                self.get_logger().error("[ID:%03d] groupSyncRead addparam failed" % sid)

    def shutdown_callback(self):
         # Clear syncread parameter storage
            self.groupSyncRead.clearParam()
            if self.portHandler.is_open:
                self.portHandler.closePort()


def main(args=None):
    rclpy.init(args=args)
    mirror = None

    try:
        mirror = Mirror()
        rclpy.spin(mirror)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        if mirror is not None:
            mirror.shutdown_callback()
            mirror.destroy_node()
        rclpy.try_shutdown()

if __name__ == '__main__':
    main()
