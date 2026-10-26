"""Behavior preview or odometry-feedback motion, selected explicitly."""
from pathlib import Path
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    share=Path(get_package_share_directory('tb4_hand_gesture'))
    return LaunchDescription([
        DeclareLaunchArgument('preview_only',default_value='true',choices=['true','false']),
        Node(package='tb4_hand_gesture',executable='robot_behavior_node',
             name='robot_behavior_node',output='screen',
             parameters=[str(share/'config/behavior.yaml'),{
                 'preview_only':ParameterValue(LaunchConfiguration('preview_only'),value_type=bool)}]),
    ])
