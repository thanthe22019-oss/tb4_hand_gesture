"""Local open arena; reuse installed TurtleBot robot spawning and controllers."""
import os
from pathlib import Path
from ament_index_python.packages import get_package_share_directory as share
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    own=Path(share('tb4_hand_gesture'))
    upstream=Path(share('turtlebot4_ignition_bringup'))
    resource_paths=[str(Path(share(p)).parent) for p in ['turtlebot4_description','irobot_create_description']]
    resource_paths += [os.environ.get('IGN_GAZEBO_RESOURCE_PATH','')]
    plugins=[str(Path(share(p))/'lib') for p in ['turtlebot4_ignition_gui_plugins','irobot_create_ignition_plugins']]
    return LaunchDescription([
        DeclareLaunchArgument('world',default_value='gesture_arena',choices=['gesture_arena']),
        DeclareLaunchArgument('rviz',default_value='false',choices=['true','false']),
        SetEnvironmentVariable('IGN_GAZEBO_RESOURCE_PATH',os.pathsep.join(resource_paths)),
        SetEnvironmentVariable('IGN_GUI_PLUGIN_PATH',os.pathsep.join(plugins)),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(str(Path(share('ros_ign_gazebo'))/'launch/ign_gazebo.launch.py')),
            launch_arguments={'ign_args':[str(own/'worlds/gesture_arena.sdf'),' -r -v 2 --gui-config ',str(upstream/'gui/standard/gui.config')]}.items()),
        Node(package='ros_gz_bridge',executable='parameter_bridge',name='clock_bridge',
             arguments=['/clock@rosgraph_msgs/msg/Clock[ignition.msgs.Clock']),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(str(upstream/'launch/turtlebot4_spawn.launch.py')),
            launch_arguments={'world':'gesture_arena','model':'standard','use_sim_time':'true',
                              'nav2':'false','slam':'false','localization':'false',
                              'rviz':LaunchConfiguration('rviz')}.items()),
    ])
