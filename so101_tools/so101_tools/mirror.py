#!/usr/bin/env python3
import math
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState

from scservo_sdk import *

# Control table address
ADDR_STS_PRESENT_POSITION  = 56
ADDR_SCS_TORQUE_ENABLE = 40

# STS3215 Servo Parameters
TICKS_PER_REV = 4096
CENTER_TICK = 2047

# Default setting
SCS_IDS                     = [1, 2, 3, 4, 5, 6]  # SCServo#1 IDs
SCS_JOINT_NAMES             = ['shoulder_pan', 'shoulder_lift', 'elbow_flex', 'wrist_flex', 'wrist_roll', 'gripper']
BAUDRATE                    = 1000000           # SCServo default baudrate : 1000000
DEVICENAME                  = '/dev/ttyACM0'    # Check which port is being used on your controller
                                                # ex) Linux: "/dev/ttyUSB0" Mac: "/dev/tty.usbserial-*"

SCS_MINIMUM_POSITION_VALUE  = 100               # SCServo will rotate between this value
SCS_MAXIMUM_POSITION_VALUE  = 4000              # and this value (note that the SCServo would not move when the position value is out of movable range. Check e-manual about the range of the SCServo you use.)
SCS_MOVING_STATUS_THRESHOLD = 20                # SCServo moving status threshold
SCS_MOVING_SPEED            = 0                 # SCServo moving speed
SCS_MOVING_ACC              = 0                 # SCServo moving acc
protocol_end                = 0                 # SCServo bit end(STS/SMS=0, SCS=1)


class Mirror(Node):
    def __init__(self):
        super().__init__('mirror')
        
        self.publisher_ = self.create_publisher(JointState, '/joint_states', 10)
        
        timer_period = 0.033  # 30Hz
        self.timer = self.create_timer(timer_period, self.timer_callback)

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
        if self.portHandler.openPort():
            self.get_logger().info("Succeeded to open the port")
        else:
            self.get_logger().error("Failed to open the port")


        # Set port baudrate
        if self.portHandler.setBaudRate(BAUDRATE):
            self.get_logger().info("Succeeded to change the baudrate")
        else:
            self.get_logger().error("Failed to change the baudrate")

        for sid in SCS_IDS:
            # Add parameter storage for SCServo#i present position value
            scs_addparam_result = self.groupSyncRead.addParam(sid)
            self.get_logger().info("[ID:%03d] groupSyncRead addparam result: %s" % (sid, scs_addparam_result))
            if scs_addparam_result != True:
                self.get_logger().error("[ID:%03d] groupSyncRead addparam failed" % sid)

    def timer_callback(self):
        
        msg = JointState()
        msg.name = [f'{name}' for name in SCS_JOINT_NAMES]
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
                continue

            scs_present_position = SCS_LOWORD(scs_present_position_speed)
            scs_present_speed = SCS_HIWORD(scs_present_position_speed)

            scs_present_position_rad = ((scs_present_position - CENTER_TICK) / TICKS_PER_REV) * (2 * math.pi)
            scs_present_speed_rad_s = (SCS_TOHOST(scs_present_speed, 15) / 4096) * (2 * math.pi)

            self.get_logger().info("Position [ID:%03d] PresPosTicks:%03d PresPosRad:%05f" % (sid, scs_present_position, scs_present_position_rad))
            self.get_logger().info("Velocity [ID:%03d] PresSpeedTicks:%03d PresSpeedRad:%05f" % (sid, SCS_TOHOST(scs_present_speed, 15), scs_present_speed_rad_s))

            msg.header.stamp = self.get_clock().now().to_msg()
            msg.position[sid - 1] = scs_present_position_rad
            msg.velocity[sid - 1] = scs_present_speed_rad_s


        self.publisher_.publish(msg)

    def shutdown_callback(self):
         # Clear syncread parameter storage
            self.groupSyncRead.clearParam()

            for sid in SCS_IDS:
                # SCServo#1 torque
                scs_comm_result, scs_error = self.packetHandler.write1ByteTxRx(self.portHandler, sid, ADDR_SCS_TORQUE_ENABLE, 0)
                if scs_comm_result != COMM_SUCCESS:
                    self.get_logger().error("%s" % self.packetHandler.getTxRxResult(scs_comm_result))
                elif scs_error != 0:
                    self.get_logger().error("%s" % self.packetHandler.getRxPacketError(scs_error))


def main(args=None):
    rclpy.init(args=args)

    mirror = Mirror()

    rclpy.spin(mirror)

    mirror.destroy_node()
    
    rclpy.shutdown()

if __name__ == '__main__':
    main()
