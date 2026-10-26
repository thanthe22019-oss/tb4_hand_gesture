"""Start recognition with an explicit Python runtime and model file."""
from pathlib import Path
import sys
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    share = Path(get_package_share_directory('tb4_hand_gesture'))
    return LaunchDescription([
        DeclareLaunchArgument('python_executable', default_value=sys.executable),
        DeclareLaunchArgument('model_path', description='Path to gesture_recognizer.task'),
        DeclareLaunchArgument('show_window', default_value='true', choices=['true', 'false']),
        DeclareLaunchArgument('camera_index', default_value='0'),
        Node(package='tb4_hand_gesture', executable='gesture_recognition_node',
             name='gesture_recognition_node', output='screen',
             prefix=[LaunchConfiguration('python_executable')],
             parameters=[str(share/'config/gesture.yaml'), {
                 'model_path': LaunchConfiguration('model_path'),
                 'show_window': ParameterValue(LaunchConfiguration('show_window'),value_type=bool),
                 'camera_index': ParameterValue(LaunchConfiguration('camera_index'),value_type=int),
             }]),
    ])
