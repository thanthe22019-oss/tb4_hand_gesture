# Milestone 3 — Máy trạng thái và watchdog

Ngày: 25/10/2026. Người dùng đã xác nhận Wave hoạt động khi thử trực tiếp trước milestone này.

## Đã thực hiện

- behavior.py: BehaviorController độc lập ROS; receive/tick/complete/snapshot, trạng thái IDLE/SELECTED/EXECUTING.
- Ánh xạ WAVE=greet, POINTING_UP=back_and_forth, VICTORY=circle.
- Chọn chưa thực thi. THUMB_UP xác nhận một lần, mỗi lần xác nhận có execution_id mới.
- OPEN_PALM/CLOSED_FIST/NO_HAND hủy và xóa lựa chọn. UNKNOWN khi EXECUTING hủy, không tự tiếp tục khi tín hiệu trở lại.
- UNKNOWN khi SELECTED được giữ lựa chọn tối đa selection_timeout=5s để người dùng chuyển tư thế; giữ cử chỉ chọn thật tiếp tục làm mới lựa chọn.
- Heartbeat timeout=0,6s; nguồn thời gian monotonic; timer 20Hz, không có chuyển động blocking.
- robot_behavior_node: subscribe /detected_gesture, publish /behavior_status và /cmd_vel zero. Stop/cancel publish ngay trong callback, không chờ timer.
- Launch behavior riêng và launch interaction chạy đồng thời nhận diện/behavior; script run_interaction.sh dùng đúng venv cho nhận diện.

## Phạm vi preview

Các profile chuyển động thuộc M4. Node M3 chủ động chỉ hỗ trợ preview_only=true, phát zero Twist ở mọi trạng thái. EXECUTING hiện có nghĩa đã xác nhận trong mô phỏng logic; chưa thực hiện chào/tiến–lùi/vòng tròn. Không có số đo robot phanh hoặc quỹ đạo vật lý ở milestone này.

## Kiểm thử thực tế

- RED trước implementation: module behavior chưa có.
- GREEN: 17 test behavior + 32 test gesture, tổng 49 PASS.
- Build package PASS; compile Python PASS; launch interaction --show-args PASS.
- ROS test dùng domain 173 riêng, không đưa cử chỉ giả vào phiên simulator của người dùng.
- Nhận 122 status và 122 Twist; toàn bộ vận tốc zero.
- Chọn/xác nhận, giữ confirm, đổi lựa chọn, stop/cancel, NO_HAND, UNKNOWN và không tự tiếp tục: PASS.
- Độ trễ nhận status IDLE/stop sau gửi OPEN_PALM: 0.0294s trong lần đo này.
- Watchdog chuyển IDLE sau 0.6293s từ bản tin cuối với cấu hình 0,6s. Có thêm chu kỳ timer và thời gian truyền; không phải cam kết realtime.
- Guard preview_only=false: thoát mã 1 với thông báo chưa hỗ trợ profile chuyển động.
- Launch shutdown sạch, exit 0.
- Kiểm tra launch tổng: Combined webcam recognition + behavior preview launch PASS, clean shutdown.

Launch tổng nhận 245 bản tin camera; nhãn quan sát gồm {'UNKNOWN': 61, 'NO_HAND': 27, 'OPEN_PALM': 47, 'WAVE': 110}. Đây không phải đánh giá accuracy có ground truth.

## File tạo/sửa

Tạo dưới src/tb4_hand_gesture/: tb4_hand_gesture/behavior.py, robot_behavior_node.py; config/behavior.yaml; launch/behavior.launch.py, interaction.launch.py; test/test_behavior.py.
Sửa setup.py để đăng ký robot_behavior_node. Tạo scripts/run_interaction.sh. Cập nhật README và tài liệu/progress/plan.
Kết quả ROS lưu milestone3_runtime.json.

## Lệnh

```bash
cd ~/Interaction/tb4_hand_gesture
./scripts/build.sh
./scripts/run_interaction.sh
```

Terminal khác: source /opt/ros/humble/setup.bash; source install/setup.bash; ros2 topic echo /behavior_status.
Test: PYTHONPATH=src/tb4_hand_gesture python3 -m unittest discover -s src/tb4_hand_gesture/test -v.

## Còn lại / bước tiếp

- Cần người dùng thử chuỗi cử chỉ thật trên launch tổng; ROS test vừa rồi dùng nhãn tổng hợp.
- M4: profile chào, tiến–lùi 4 chu kỳ, vòng tròn; kiểm tra khu vực trống, Gazebo/odom và controller watchdog khi behavior node chết.
- M5: thử tích hợp động tác thật, mất tay, nhiễu và pause/reset khi robot chuyển động.
- Không commit/push.
