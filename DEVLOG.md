# Dev log

Dated entries: what I did, what broke, the fix.

11/3/26:

Updated .urdf file to use correct project directories. Originally updated the paths to be relative file paths but RViz couldnt find the mesh files. Fixed this by using ROS package:// path.

Created launch file that runs robot_state_publisher, robot_joint_publisher_gui, and rviz.

Rviz sucessfully displays the robot and the joint sliders correctly adjust the joints. When centering every joint at 0, the robot looks correct with a small exception. Gripper at 0 rad is almost closed but not fully. URDF range is −10deg to 100deg, so closed is at the lower limit. LeRobot uses 0–100 for the gripper. Check in issue 2.

Elbow flex goes too far at 1.69 rad and model collapses into itself but is fine at -1.69 rad. This is based off of rviz visuals only. More testing will be done in issue 2.

11/4/26

I need to use feetech-servo-sdk python library which can't be installed with rosdep. To get this working I had to use a venv which also contains the system packages that ros depends on. The venv is in the project root (~/Robotics/so-arm101_ws/.venv). In order for colcon to build using this python we first have to source our system ros, then the venv, then run the command 'python -m colcon build --symlink-install', then source the ws. TODO: Add this info in project quickstart README.

11/5/26

Today I learned a bit about hardware. I learned that my servos are connected to eachother via one wire, from one servo to the other (daisy chaining). The way the servos communicate is via packets and registers. Registers are essentially different memory addresses that hold some information about the respective servo, ie: torque enable, current position, or current speed. Each of these registers has a different memory address, size, and is either stored in RAM or in persistent memory (EEPROM Register). The table defining all of these registers is called the memory table.

HIWORD and LOWORD are the top and bottom halves of a word which is a string of bits, ie: LOWORD of a 4 byte word gives us the bottom half of data. This is useful when data you need is stored sequentially in the memory.

Baudrate tells us how how fast bits are sent over the serial wire. In this case it is defined as bits per second.

11/18/26

I learned how to use the sdk example code to read the servos raw positions. I then adapted the code to work inside the mirror node. The JointState msg uses radians and rad / s for its values. I converted each raw tick value by googling the conversion. Initially I created my own names for the name field in JointState but realized that that was wrong and looked at the urdf for each proper joint name. I also learned about signs being important for the direction of the joints movement but in this case every sign is just +1.

I also learned about homing offsets and how the arms calibration is done to figure out each joints 0 (middle position) and min / max range of motion values. I looked at the calibration json file to check my joints actual limits and compared them to the urdf. All of the urdf limits except the elbow were slightly smaller than the actual range which is okay. However the elbow's urdf limit went beyond the actual so i tightened it. This explains the issue from 11/3/26 where the slider allowed the rviz model to collide into itself.

11/20

RECAP
We start with our physical robot, a description of our robot (urdf), and a way to display the robot in rviz using that description. The URDF describes the robot's links, joints, and joint limits. The first step was displaying the robot in rviz and using the ros2 joint state gui and robot state publisher to move the robot in rviz using the gui (display.launch.py).

Next was reading the robot's state from the physical robot and mirroring it in rviz rather than reading joint positions from the fake robot state pub and joint state gui. This invloved using the feetch servo sdk to read each joint state and converting the raw ticks (position) to something the robot state publisher can understand, radians. To convert to radius we had to understand how the robot was originally calibrated using lerobot's calibration script. This script found where each servo's center position is relative to the robot's physical joint limits. We then compared the robot's actual joint limits to the URDF's joint limits to ensure the robot will never try to move to an invalid position and damage the servos.

The next and current step is to create a way for a controller to talk to a hardware driver to actually move our robot. To do this we use ros2_control. This ros2 framework acts as a controller manager or a bridge between our controller and our driver. The controller tells the robot how it should move, and the driver talks to the actual servos to reach our desired position.
