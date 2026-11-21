"""Show the SO-101 model in RViz, with sliders to move each joint.

Usage:
  ros2 launch so101_description display.launch.py
  ros2 launch so101_description display.launch.py model:=/path/to/other.urdf
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    # Path to this package in install/.../share/so101_description, not in src/.
    # That's why the install() rule in CMakeLists.txt matters.
    pkg_share = FindPackageShare('so101_description')

    model_arg = DeclareLaunchArgument(
        'model',
        default_value=PathJoinSubstitution([pkg_share, 'urdf', 'so101_model.urdf.xacro']),
        description='Absolute path to the robot URDF or xacro file',
    )
    rviz_config_arg = DeclareLaunchArgument(
        'rviz_config',
        default_value=PathJoinSubstitution([pkg_share, 'rviz', 'display.rviz']),
        description='Absolute path to the RViz config file',
    )

    # Run xacro on the file and use its output (the URDF text) as the parameter value.
    # ParameterValue(..., value_type=str) stops ROS from trying to parse the XML as YAML.
    robot_description = ParameterValue(
        Command(['xacro ', LaunchConfiguration('model')]),
        value_type=str,
    )

    # Reads robot_description + /joint_states, computes forward kinematics, and
    # publishes every link's pose on /tf. It also republishes the URDF on the
    # /robot_description topic, which is where RViz's RobotModel display reads it.
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': robot_description}],
        output='screen',
    )

    # A slider window for each movable joint. It publishes /joint_states.
    joint_state_publisher_gui = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
    )

    # RViz, loading your saved config (-d)
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', LaunchConfiguration('rviz_config')],
        output='screen',
    )

    return LaunchDescription([
        model_arg,
        rviz_config_arg,
        robot_state_publisher,
        joint_state_publisher_gui,
        rviz,
    ])
