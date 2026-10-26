# Milestone 0 — Inspect, 25/10/2026

## Kiểm tra thực tế

- Ubuntu 22.04.5 LTS; Python 3.10.12.
- ROS Humble tại /opt/ros/humble. rclpy import được sau source setup.bash.
- turtlebot4_ignition_bringup và irobot_create_nodes được ament index tìm thấy trong /opt/ros/humble/share.
- ros-humble-turtlebot4-simulator: 1.0.3-1jammy.20261006.004227.
- OpenCV hệ thống 4.5.4. MediaPipe chưa cài trong Python hệ thống.
- Webcam /dev/video0 và /dev/video1 có trên host. OpenCV mở video0 thành công và đọc frame 640x480 BGR; không lưu ảnh.
- ROS graph kiểm tra bằng ros2 topic list --no-daemon --spin-time 3 chỉ có /parameter_events và /rosout.
- Không thấy process simulator/RViz đang chạy trong lần kiểm tra host. Chưa test robot runtime.

## Existing project

~/Interaction/tb4_nav2 có launch wrapper chạy warehouse kèm Nav2/AMCL/map. Bài 6 không cần stack navigation này.
Launch gốc /opt/ros/humble/share/turtlebot4_ignition_bringup/launch/turtlebot4_ignition.launch.py có world, model, rviz; cần kiểm tra đầy đủ launch arguments trước tạo wrapper.
Bridge irobot_create_ignition_bringup/launch/create3_ros_ignition_bridge.launch.py có cmd_vel và diffdrive_controller/cmd_vel_unstamped.
control.yaml có cmd_vel_timeout 0.5 s. Đây là cấu hình file, chưa xác minh tham số runtime.

## Missing / risks

- Chưa có MediaPipe hoặc model gesture_recognizer.task cho workspace mới.
- Cần venv riêng và chốt dependency sau test import MediaPipe + rclpy, tránh xung đột NumPy/OpenCV.
- Hai /dev/video không khẳng định hai webcam độc lập; mới test video0.
- Chưa kiểm tra subscriber /cmd_vel, action undock, odometry và robot di chuyển.
- Chưa kiểm thử nhận diện Wave hoặc hành vi, không có số liệu accuracy/FPS/latency.
- Chưa xác minh version Gazebo runtime bằng lệnh simulator.

## Deliverable

Chỉ tạo tài liệu kế hoạch/Inspect trong folder mới. Chưa cài dependency, sửa cấu hình cũ, tạo node hoặc commit.
Milestone tiếp theo: chạy simulator và webcam độc lập, kiểm chứng vận tốc có thời hạn trước tích hợp nhận diện.
