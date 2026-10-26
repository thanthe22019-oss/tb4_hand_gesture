# Milestone 4 — Chuyển động Gazebo, 26/10/2026

## Đã triển khai

- MotionExecutor: ba profile odometry-feedback, không phụ thuộc ROS.
- Chào: +30°, -60°, +30°. Tiến–lùi: 4 cặp ±0,2 m. Circle: một vòng, bán kính 0,4 m.
- Tốc độ giới hạn 0,08 m/s và 0,35 rad/s; giảm tốc gần đích, nghỉ 0,4s giữa các đoạn; timeout 60s/đoạn.
- RobotBehaviorNode dùng pose mới, kiểm tra quaternion/giá trị hữu hạn, timeout odom, timestamp lùi/lặp và nhảy pose.
- Stop/cancel, mất tay hoặc UNKNOWN đang chạy xóa profile; không tự tiếp tục.
- preview_only vẫn mặc định true. Bật profile bằng preview_only:=false.
- Sân gesture_arena.sdf riêng 20×20m; tái sử dụng spawning/controllers gốc, không sửa package đã cài.

## Test logic và ROS fault injection

- RED: chưa có module motion. Test circle phát hiện timeout 30s ngắn hơn thời gian đi vòng (~31,4s lý tưởng); tăng timeout có giới hạn lên 60s.
- GREEN: 57 unittest PASS (32 gesture, 17 behavior, 8 motion).
- ROS domain 174 riêng không có robot: thiếu odometry từ chối chạy; giữ heartbeat nhưng lặp timestamp odom phải hủy; timestamp reset hủy; dữ liệu quay lại không tự chạy. PASS.
- Test lặp timestamp từng FAIL, sau sửa chỉ refresh watchdog khi stamp tiến mới thì PASS.
- Các test ROS tổng hợp là kiểm tra kỹ thuật, không thay thế demo cử chỉ thật.

## Kiểm thử Gazebo thực tế

Domain 173 và IGN partition riêng; robot undock thành công trước thử. Lệnh hành vi được gửi bằng nhãn ROS tổng hợp và heartbeat, không dùng camera trong phép đo này.

| Hành vi | Thời gian thực (s) | Tổng đường đi odom (m) | Sai lệch vị trí cuối (m) | Sai lệch hướng cuối (rad) | Đoạn đã chạy |
| --- | --- | --- | --- | --- | --- |
| greet | 12.47 | 0.0000 | 0.0000 | 0.0226 | 3 |
| back_and_forth | 32.99 | 1.5480 | 0.0008 | 0.0000 | 8 |
| circle | 35.64 | 2.5024 | 0.0109 | 0.0220 | 1 |

Sai lệch tính so với pose bắt đầu từng hành vi; không có ground-truth đánh giá accuracy. Dữ liệu đầy đủ tại milestone4_motion.json. Giá trị rất nhỏ ở chào chỉ phản ánh mô phỏng/odometry, không phải độ chính xác robot thật.

## Dừng và watchdog

- Open Palm giữa vòng tròn: IDLE/stop sau 0.0525s trong lần đo; kiểm tra odom sau 1s xác nhận vận tốc gần zero.
- Mất gesture heartbeat khi đang di chuyển: hủy sau 0.6159s với cấu hình 0,6s; odom sau đó xác nhận đứng yên.
- Tắt cưỡng bức riêng process group behavior kiểm thử khi robot đang chạy: controller đưa vận tốc về ngưỡng đứng yên sau 0.6554s.
- Threshold test đứng yên: |linear|<0,01 m/s và |angular|<0,02 rad/s ở test node-kill. Dữ liệu milestone4_stop.json.
- Các giá trị là kết quả một lần chạy, không phải cam kết realtime.

## Lỗi thực tế đã xử lý

1. World đầu tiên khai báo Sensors trùng với robot URDF, gây render/GL crash. Bỏ plugin trùng trong world riêng; không đổi plugin robot cài sẵn. Sân sau đó chạy đủ profile.
2. Create 3 báo Reached backup limit và chặn lượt lùi. Trong sân trống mô phỏng, sau undock đặt safety_override=backup_only. Không tắt toàn bộ safety. README ghi rõ bước setup này.
3. Subscriber odometry nội bộ chưa discovery xong khi probe đã gửi confirm. Thêm odometry_ready và chờ readiness trước kiểm thử; không bỏ guard hoặc hạ yêu cầu dữ liệu mới.

## File tạo/sửa

Tạo motion.py, test/test_motion.py, worlds/gesture_arena.sdf, launch/arena.launch.py.
Sửa robot_behavior_node.py, behavior.py (cancel), launch/behavior.launch.py, launch/interaction.launch.py, config/behavior.yaml, setup.py, package.xml.
Cập nhật README, plan/progress, và JSON minh chứng. Các file source nằm trong src/tb4_hand_gesture/.

## Build/chạy và bước tiếp

Xem README: scripts/build.sh; arena.launch.py; /undock; đặt backup_only trong sân mô phỏng; scripts/run_interaction.sh preview_only:=false.
M5 còn lại: demo tất cả hành vi bằng cử chỉ thật, thử nhiễu/mất tay/camera, pause/reset và ghi video/ảnh. M4 không tuyên bố đã hoàn thành demo bằng webcam.
Chưa commit/push.
