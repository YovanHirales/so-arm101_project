# Dev log

Dated entries: what I did, what broke, the fix.

11/3/26:

Updated .urdf file to use correct project directories. Originally updated the paths to be relative file paths but RViz couldnt find the mesh files. Fixed this by using ROS package:// path.

Created launch file that runs robot_state_publisher, robot_joint_publisher_gui, and rviz.

Rviz sucessfully displays the robot and the joint sliders correctly adjust the joints. When centering every joint at 0, the robot looks correct with a small exception. Gripper at 0 rad is almost closed but not fully. URDF range is −10deg to 100deg, so closed is at the lower limit. LeRobot uses 0–100 for the gripper. Check in step 2.
