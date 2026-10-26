"""Use the installed simulator without navigation or map localization."""
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from pathlib import Path


def generate_launch_description():
    upstream = Path(get_package_share_directory('turtlebot4_ignition_bringup'))
    return LaunchDescription([
        DeclareLaunchArgument('world', default_value='warehouse'),
        DeclareLaunchArgument('rviz', default_value='false', choices=['true', 'false']),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(str(upstream / 'launch/turtlebot4_ignition.launch.py')),
            launch_arguments={
                'world': LaunchConfiguration('world'),
                'model': 'standard',
                'rviz': LaunchConfiguration('rviz'),
                'nav2': 'false', 'slam': 'false', 'localization': 'false',
                'use_sim_time': 'true',
            }.items(),
        ),
    ])
