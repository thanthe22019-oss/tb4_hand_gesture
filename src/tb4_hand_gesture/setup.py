from glob import glob
from setuptools import find_packages, setup

setup(
    name='tb4_hand_gesture', version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/tb4_hand_gesture']),
        ('share/tb4_hand_gesture', ['package.xml']),
        ('share/tb4_hand_gesture/launch', glob('launch/*.launch.py')),
        ('share/tb4_hand_gesture/config', glob('config/*.yaml')),
        ('share/tb4_hand_gesture/worlds', glob('worlds/*.sdf')),
    ],
    install_requires=['setuptools'], zip_safe=True,
    maintainer='Student 23020730', maintainer_email='student@example.com',
    description='TurtleBot 4 hand gesture interaction', license='Apache-2.0',
    entry_points={'console_scripts': [
        'webcam_check = tb4_hand_gesture.webcam_check:main',
        'gesture_recognition_node = tb4_hand_gesture.gesture_recognition_node:main',
        'robot_behavior_node = tb4_hand_gesture.robot_behavior_node:main',
    ]},
)
