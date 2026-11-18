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
