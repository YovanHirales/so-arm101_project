"""Bring up the SO-101 with ros2_control: controllers, hardware, and RViz.

Usage:
  ros2 launch so101_bringup bringup.launch.py              # mock hardware (default)
  ros2 launch so101_bringup bringup.launch.py mode:=real   # real arm (step 5, once the C++ driver exists)
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    # Two packages now: the model lives in so101_description, the controller config here.
    description_share = FindPackageShare('so101_description')
    bringup_share = FindPackageShare('so101_bringup')

    model_arg = DeclareLaunchArgument(
        'model',
        default_value=PathJoinSubstitution([description_share, 'urdf', 'so101_model.urdf.xacro']),
        description='Absolute path to the robot xacro file',
    )
    rviz_config_arg = DeclareLaunchArgument(
        'rviz_config',
        default_value=PathJoinSubstitution([description_share, 'rviz', 'display.rviz']),
        description='Absolute path to the RViz config file',
    )
    mode_arg = DeclareLaunchArgument(
        'mode',
        default_value='mock',
        choices=['mock', 'real'],
        description='Hardware to use: mock (fake, echoes commands) or real (the arm)',
    )

    # Runs: xacro <model> mode:=<mode>
    # The list items are joined into one command, so the spaces inside the strings matter.
    # mode picks the <plugin> inside the <ros2_control> block (see so101.ros2_control.xacro).
    robot_description = ParameterValue(
        Command(['xacro ', LaunchConfiguration('model'), ' mode:=', LaunchConfiguration('mode')]),
        value_type=str,
    )

    # Publishes TF from /joint_states, and republishes the URDF on the /robot_description topic.
    # The controller manager reads the URDF (including the <ros2_control> block) from that topic.
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': robot_description}],
        output='screen',
    )

    # The controller manager: loads the hardware plugin named in the URDF, then runs the
    # read -> update controllers -> write loop at update_rate from controllers.yaml.
    controller_manager = Node(
        package='controller_manager',
        executable='ros2_control_node',
        parameters=[PathJoinSubstitution([bringup_share, 'config', 'controllers.yaml'])],
        output='screen',
    )

    # Spawners ask the controller manager to load, configure, and activate one controller each.
    # They wait for the controller manager to come up, then exit once their controller is active.
    joint_state_broadcaster_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster'],
        output='screen',
    )
    joint_trajectory_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_trajectory_controller'],
        output='screen',
    )

    rviz = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', LaunchConfiguration('rviz_config')],
        output='screen',
    )

    return LaunchDescription([
        model_arg,
        rviz_config_arg,
        mode_arg,
        robot_state_publisher,
        controller_manager,
        joint_state_broadcaster_spawner,
        joint_trajectory_controller_spawner,
        rviz,
    ])
