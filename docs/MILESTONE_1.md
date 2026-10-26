# Milestone 1 — Simulation và webcam

Ngày kiểm thử: 25/10/2026. Workspace độc lập ~/Interaction/tb4_hand_gesture.

## Đã thực hiện

- Tạo package ament_python tb4_hand_gesture, build thành công (1 package).
- Wrapper simulation.launch.py gọi simulator cài sẵn; nav2/slam/localization=false, rviz=false.
- Tạo webcam_check: preview OpenCV, kiểm tra headless có thời hạn, không lưu ảnh/không điều khiển robot.
- Venv --system-site-packages riêng. MediaPipe 0.10.32, NumPy 1.26.4, OpenCV contrib 4.11.0.86.
- Kiểm tra import MediaPipe Tasks, rclpy và cv_bridge trong cùng interpreter: PASS.
- Model Gesture Recognizer chính thức nạp và inference ảnh đen thành công, phát hiện 0 bàn tay. Không phải bằng chứng nhận diện bàn tay thật.

## Kết quả thực tế

- ros2 launch ... --show-args: PASS.
- Webcam headless: 141 frame / 5,04 giây.
- Webcam GUI mở và đóng bình thường: 159 frame / 6,01 giây. Không lưu video/ảnh.
- Gazebo warehouse khởi động; /undock trả SUCCEEDED, is_docked=false.
- /cmd_vel có subscriber, nguồn bridge simulator; không chạy Nav2/teleop.
- Probe tạm gửi linear.x=0,05 m/s trong 2 giây rồi gửi zero Twist.
- Odometry dịch chuyển 0,0967851 m; dịch thêm 0,0020649 m trong giai đoạn dừng.
- Vận tốc cuối linear.x=-3,35e-17 m/s, angular.z=-2,71e-16 rad/s, coi như 0.
- Dữ liệu trước/sau được lưu trong milestone1_motion.json.
- Kiểm thử vận tốc là lệnh setup bằng script tạm, không phải phương thức điều khiển khi demo cử chỉ.

## Lưu ý và giới hạn

- Probe đầu tiên chưa chờ đủ discovery odometry/subscriber nên từ chối phát vận tốc. Chờ cả hai tối đa 15 giây rồi thử lại thành công.
- Gazebo có cảnh báo update period controller 0,001 s so với physics 0,003 s; chuyển động thử vẫn thực hiện. Không sửa cấu hình cài sẵn.
- Turtlebot4_node báo các service OAKD/RPLIDAR start/stop unavailable. Bài dùng webcam laptop, không dựa vào camera OAKD. Cần xử lý nếu milestone sau cần những sensor đó.
- Chưa đo vùng trống cho vòng tròn/tiến–lùi dài. M1 chỉ thử 10 cm sau undock; M4 phải xác nhận đủ khoảng trống.
- Chưa kiểm chứng runtime controller watchdog; nhiệm vụ M4.
- Chưa có gesture_recognition_node/robot_behavior_node; chưa kiểm thử 6 cử chỉ hoặc hành vi.
- Không commit/push.

## Lệnh build/chạy

Xem README.md ở root: scripts/build.sh, scripts/setup_gesture_venv.sh,
ros2 launch tb4_hand_gesture simulation.launch.py và webcam_check.

## Milestone kế tiếp

M2: nhận 5 tư thế MediaPipe + Wave theo thời gian; overlay và publish /detected_gesture.
