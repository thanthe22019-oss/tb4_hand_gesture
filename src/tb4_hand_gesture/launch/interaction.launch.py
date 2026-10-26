"""Run webcam recognition and Milestone 3 behavior preview together."""
from pathlib import Path
import sys
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    share=Path(get_package_share_directory('tb4_hand_gesture'))
    return LaunchDescription([
        DeclareLaunchArgument('python_executable',default_value=sys.executable),
        DeclareLaunchArgument('model_path',description='Path to gesture_recognizer.task'),
        DeclareLaunchArgument('show_window',default_value='true',choices=['true','false']),
        DeclareLaunchArgument('camera_index',default_value='0'),
        DeclareLaunchArgument('preview_only',default_value='true',choices=['true','false']),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(str(share/'launch/recognition.launch.py')),
            launch_arguments={name:LaunchConfiguration(name) for name in
                              ['python_executable','model_path','show_window','camera_index']}.items()),
        IncludeLaunchDescription(PythonLaunchDescriptionSource(str(share/'launch/behavior.launch.py')),
                                 launch_arguments={'preview_only':LaunchConfiguration('preview_only')}.items()),
    ])
