#!/usr/bin/env python
#
# *********     Sync Read and Sync Write Example      *********
#
#
# Available SCServo model on this example : All models using Protocol SCS
# This example is tested with a SCServo(STS/SMS), and an URT
# Be sure that SCServo(STS/SMS) properties are already set as %% ID : 1 / Baudnum : 6 (Baudrate : 1000000)
#

import os

if os.name == 'nt':
    import msvcrt
    def getch():
        return msvcrt.getch().decode()
else:
    import sys, tty, termios
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    def getch():
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

from scservo_sdk import *                    # Uses SCServo SDK library

# Control table address
ADDR_STS_PRESENT_POSITION  = 56
ADDR_SCS_TORQUE_ENABLE = 40

# Default setting
SCS1_ID                     = 1                 # SCServo#1 ID : 1
SCS2_ID                     = 2                 # SCServo#1 ID : 2
SCS3_ID                     = 3                 # SCServo#1 ID : 3
SCS4_ID                     = 4                 # SCServo#1 ID : 4
SCS5_ID                     = 5                 # SCServo#1 ID : 5
SCS6_ID                     = 6                 # SCServo#1 ID : 6
BAUDRATE                    = 1000000           # SCServo default baudrate : 1000000
DEVICENAME                  = '/dev/ttyACM0'    # Check which port is being used on your controller
                                                # ex) Windows: "COM1"   Linux: "/dev/ttyUSB0" Mac: "/dev/tty.usbserial-*"

SCS_MINIMUM_POSITION_VALUE  = 100               # SCServo will rotate between this value
SCS_MAXIMUM_POSITION_VALUE  = 4000              # and this value (note that the SCServo would not move when the position value is out of movable range. Check e-manual about the range of the SCServo you use.)
SCS_MOVING_STATUS_THRESHOLD = 20                # SCServo moving status threshold
SCS_MOVING_SPEED            = 0                 # SCServo moving speed
SCS_MOVING_ACC              = 0                 # SCServo moving acc
protocol_end                = 0                 # SCServo bit end(STS/SMS=0, SCS=1)

index = 0
scs_goal_position = [SCS_MINIMUM_POSITION_VALUE, SCS_MAXIMUM_POSITION_VALUE]         # Goal position

# Initialize PortHandler instance
# Set the port path
# Get methods and members of PortHandlerLinux or PortHandlerWindows
portHandler = PortHandler(DEVICENAME)

# Initialize PacketHandler instance
# Get methods and members of Protocol
packetHandler = PacketHandler(protocol_end)

# Initialize GroupSyncRead instace for Present Position
groupSyncRead = GroupSyncRead(portHandler, packetHandler, ADDR_STS_PRESENT_POSITION, 4)

# Open port
if portHandler.openPort():
    print("Succeeded to open the port")
else:
    print("Failed to open the port")
    print("Press any key to terminate...")
    quit()


# Set port baudrate
if portHandler.setBaudRate(BAUDRATE):
    print("Succeeded to change the baudrate")
else:
    print("Failed to change the baudrate")
    print("Press any key to terminate...")
    quit()

# Add parameter storage for SCServo#1 present position value
scs_addparam_result = groupSyncRead.addParam(SCS1_ID)
if scs_addparam_result != True:
    print("[ID:%03d] groupSyncRead addparam failed" % SCS1_ID)
    quit()

# Add parameter storage for SCServo#2 present position value
scs_addparam_result = groupSyncRead.addParam(SCS2_ID)
if scs_addparam_result != True:
    print("[ID:%03d] groupSyncRead addparam failed" % SCS2_ID)
    quit()

# Add parameter storage for SCServo#3 present position value
scs_addparam_result = groupSyncRead.addParam(SCS3_ID)
if scs_addparam_result != True:
    print("[ID:%03d] groupSyncRead addparam failed" % SCS3_ID)
    quit()

# Add parameter storage for SCServo#4 present position value
scs_addparam_result = groupSyncRead.addParam(SCS4_ID)
if scs_addparam_result != True:
    print("[ID:%03d] groupSyncRead addparam failed" % SCS4_ID)
    quit()

# Add parameter storage for SCServo#5 present position value
scs_addparam_result = groupSyncRead.addParam(SCS5_ID)
if scs_addparam_result != True:
    print("[ID:%03d] groupSyncRead addparam failed" % SCS5_ID)
    quit()

# Add parameter storage for SCServo#6 present position value
scs_addparam_result = groupSyncRead.addParam(SCS6_ID)
if scs_addparam_result != True:
    print("[ID:%03d] groupSyncRead addparam failed" % SCS6_ID)
    quit()

while 1:
    print("Press any key to continue! (or press ESC to quit!)")
    if getch() == chr(0x1b):
        break

    # Syncread present position
    scs_comm_result = groupSyncRead.txRxPacket()
    if scs_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(scs_comm_result))

    # Check if groupsyncread data of SCServo#1 is available
    scs_getdata_result = groupSyncRead.isAvailable(SCS1_ID, ADDR_STS_PRESENT_POSITION, 4)
    scs1_present_position_speed = 0
    scs2_present_position_speed = 0
    if scs_getdata_result == True:
        # Get SCServo#1 present position value
        scs1_present_position_speed = groupSyncRead.getData(SCS1_ID, ADDR_STS_PRESENT_POSITION, 4)
    else:
        print("[ID:%03d] groupSyncRead getdata failed" % SCS1_ID)

    # Check if groupsyncread data of SCServo#2 is available
    scs_getdata_result = groupSyncRead.isAvailable(SCS2_ID, ADDR_STS_PRESENT_POSITION, 4)
    if scs_getdata_result == True:
        # Get SCServo#2 present position value
        scs2_present_position_speed = groupSyncRead.getData(SCS2_ID, ADDR_STS_PRESENT_POSITION, 4)
    else:
        print("[ID:%03d] groupSyncRead getdata failed" % SCS2_ID)

    # Check if groupsyncread data of SCServo#3 is available
    scs_getdata_result = groupSyncRead.isAvailable(SCS3_ID, ADDR_STS_PRESENT_POSITION, 4)
    if scs_getdata_result == True:
        # Get SCServo#2 present position value
        scs3_present_position_speed = groupSyncRead.getData(SCS3_ID, ADDR_STS_PRESENT_POSITION, 4)
    else:
        print("[ID:%03d] groupSyncRead getdata failed" % SCS3_ID)

    # Check if groupsyncread data of SCServo#4 is available
    scs_getdata_result = groupSyncRead.isAvailable(SCS4_ID, ADDR_STS_PRESENT_POSITION, 4)
    if scs_getdata_result == True:
        # Get SCServo#2 present position value
        scs4_present_position_speed = groupSyncRead.getData(SCS4_ID, ADDR_STS_PRESENT_POSITION, 4)
    else:
        print("[ID:%03d] groupSyncRead getdata failed" % SCS4_ID)

    # Check if groupsyncread data of SCServo#5 is available
    scs_getdata_result = groupSyncRead.isAvailable(SCS5_ID, ADDR_STS_PRESENT_POSITION, 4)
    if scs_getdata_result == True:
        # Get SCServo#2 present position value
        scs5_present_position_speed = groupSyncRead.getData(SCS5_ID, ADDR_STS_PRESENT_POSITION, 4)
    else:
        print("[ID:%03d] groupSyncRead getdata failed" % SCS5_ID)

    # Check if groupsyncread data of SCServo#6 is available
    scs_getdata_result = groupSyncRead.isAvailable(SCS6_ID, ADDR_STS_PRESENT_POSITION, 4)
    if scs_getdata_result == True:
        # Get SCServo#2 present position value
        scs6_present_position_speed = groupSyncRead.getData(SCS6_ID, ADDR_STS_PRESENT_POSITION, 4)
    else:
        print("[ID:%03d] groupSyncRead getdata failed" % SCS6_ID)

    scs1_present_position = SCS_LOWORD(scs1_present_position_speed)
    scs1_present_speed = SCS_HIWORD(scs1_present_position_speed)

    scs2_present_position = SCS_LOWORD(scs2_present_position_speed)
    scs2_present_speed = SCS_HIWORD(scs2_present_position_speed)

    scs3_present_position = SCS_LOWORD(scs3_present_position_speed)
    scs3_present_speed = SCS_HIWORD(scs3_present_position_speed)

    scs4_present_position = SCS_LOWORD(scs4_present_position_speed)
    scs4_present_speed = SCS_HIWORD(scs4_present_position_speed)

    scs5_present_position = SCS_LOWORD(scs5_present_position_speed)
    scs5_present_speed = SCS_HIWORD(scs5_present_position_speed)

    scs6_present_position = SCS_LOWORD(scs6_present_position_speed)
    scs6_present_speed = SCS_HIWORD(scs6_present_position_speed)

    print("[ID:%03d] PresPos:%03d PresSpd:%03d" % (SCS1_ID, scs1_present_position, SCS_TOHOST(scs1_present_speed, 15)))
    print("[ID:%03d] PresPos:%03d PresSpd:%03d" % (SCS2_ID, scs2_present_position, SCS_TOHOST(scs2_present_speed, 15)))
    print("[ID:%03d] PresPos:%03d PresSpd:%03d" % (SCS3_ID, scs3_present_position, SCS_TOHOST(scs3_present_speed, 15)))
    print("[ID:%03d] PresPos:%03d PresSpd:%03d" % (SCS4_ID, scs4_present_position, SCS_TOHOST(scs4_present_speed, 15)))
    print("[ID:%03d] PresPos:%03d PresSpd:%03d" % (SCS5_ID, scs5_present_position, SCS_TOHOST(scs5_present_speed, 15)))
    print("[ID:%03d] PresPos:%03d PresSpd:%03d" % (SCS6_ID, scs6_present_position, SCS_TOHOST(scs6_present_speed, 15)))

# Clear syncread parameter storage
groupSyncRead.clearParam()

# SCServo#1 torque
scs_comm_result, scs_error = packetHandler.write1ByteTxRx(portHandler, SCS1_ID, ADDR_SCS_TORQUE_ENABLE, 0)
if scs_comm_result != COMM_SUCCESS:
    print("%s" % packetHandler.getTxRxResult(scs_comm_result))
elif scs_error != 0:
    print("%s" % packetHandler.getRxPacketError(scs_error))

# SCServo#2 torque
scs_comm_result, scs_error = packetHandler.write1ByteTxRx(portHandler, SCS2_ID, ADDR_SCS_TORQUE_ENABLE, 0)
if scs_comm_result != COMM_SUCCESS:
    print("%s" % packetHandler.getTxRxResult(scs_comm_result))
elif scs_error != 0:
    print("%s" % packetHandler.getRxPacketError(scs_error))

# SCServo#3 torque
scs_comm_result, scs_error = packetHandler.write1ByteTxRx(portHandler, SCS3_ID, ADDR_SCS_TORQUE_ENABLE, 0)
if scs_comm_result != COMM_SUCCESS:
    print("%s" % packetHandler.getTxRxResult(scs_comm_result))
elif scs_error != 0:
    print("%s" % packetHandler.getRxPacketError(scs_error))

# SCServo#4 torque
scs_comm_result, scs_error = packetHandler.write1ByteTxRx(portHandler, SCS4_ID, ADDR_SCS_TORQUE_ENABLE, 0)
if scs_comm_result != COMM_SUCCESS:
    print("%s" % packetHandler.getTxRxResult(scs_comm_result))
elif scs_error != 0:
    print("%s" % packetHandler.getRxPacketError(scs_error))

# SCServo#5 torque
scs_comm_result, scs_error = packetHandler.write1ByteTxRx(portHandler, SCS5_ID, ADDR_SCS_TORQUE_ENABLE, 0)
if scs_comm_result != COMM_SUCCESS:
    print("%s" % packetHandler.getTxRxResult(scs_comm_result))
elif scs_error != 0:
    print("%s" % packetHandler.getRxPacketError(scs_error))

# SCServo#6 torque
scs_comm_result, scs_error = packetHandler.write1ByteTxRx(portHandler, SCS6_ID, ADDR_SCS_TORQUE_ENABLE, 0)
if scs_comm_result != COMM_SUCCESS:
    print("%s" % packetHandler.getTxRxResult(scs_comm_result))
elif scs_error != 0:
    print("%s" % packetHandler.getRxPacketError(scs_error))

# Close port
portHandler.closePort()