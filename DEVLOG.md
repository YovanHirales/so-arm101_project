# Dev log

Dated entries: what I did, what broke, the fix.

11/3/26:
Updated .urdf file to use correct project directories. Originally updated the paths to be relative file paths but RViz couldnt find the mesh files. Fixed this by using ROS package:// path.
