# TurtleBot 4 Hand Gesture — Implementation Plan

> For agentic workers: use superpowers:executing-plans to implement milestone by milestone. No automatic commits. User approved the design in chat on 2026-10-25.

**Goal:** Điều khiển TurtleBot 4 trong Gazebo bằng 6 cử chỉ webcam theo Bài 6.
**Architecture:** MediaPipe Gesture Recognizer phân loại tư thế, Wave nhận biết theo lịch sử landmark. Hai ROS node trao đổi qua /detected_gesture; behavior node điều khiển /cmd_vel bằng timer.
**Tech stack:** Ubuntu 22.04, ROS 2 Humble, Python 3.10, OpenCV, MediaPipe Tasks, Ignition Gazebo.
**Spec:** Phương án được người dùng duyệt trong hội thoại; yêu cầu và quyết định được ghi dưới đây.

## Constraints and approved decisions

- Workspace riêng ~/Interaction/tb4_hand_gesture; không sửa dự án tb4_nav2 hoặc cấu hình /opt/ros.
- Không cần Nav2/AMCL/map. Không chạy nguồn teleop/Nav2 cùng nguồn gesture.
- Wave chọn chào; Pointing_Up chọn tiến–lùi 4 chu kỳ; Victory chọn vòng tròn.
- Thumb_Up xác nhận một lần. Open_Palm dừng và xóa lựa chọn. Closed_Fist hủy, về chờ.
- Mọi hành vi chuyển động, gồm chào, cần xác nhận.
- Mất tay, camera lỗi hoặc mất heartbeat phải dừng; không tự tiếp tục khi có tín hiệu lại.
- Dependency nhận diện đặt trong venv riêng tương thích rclpy. Không pip nâng cấp Python hệ thống.
- Không commit/push tự động; chỉ ghi kết quả đã kiểm thử.

## Review focus

1. Open_Palm/Wave trùng tư thế: ưu tiên dừng; Wave chỉ chọn, không chuyển động.
2. Giữ Thumb_Up: chỉ thực thi một lần; cần rời tư thế rồi mới kích hoạt lại.
3. Mất tay/node treo: heartbeat không được làm dữ liệu cũ trở thành mới; watchdog dùng monotonic time.
4. Hai tay/xung đột cử chỉ: dừng, không tự chọn tay có lệnh chạy.
5. Mô phỏng pause/reset: không tích lũy quãng chạy; watchdog thực tế vẫn có hiệu lực.

## Files planned

- src/tb4_hand_gesture/package.xml, setup.py, setup.cfg, resource/tb4_hand_gesture: package ament_python.
- tb4_hand_gesture/gesture_recognition_node.py: webcam, MediaPipe, overlay, publish.
- tb4_hand_gesture/gesture_filter.py: lọc thời gian, Wave, cạnh kích hoạt.
- tb4_hand_gesture/behavior.py: máy trạng thái thuần Python và sinh vận tốc.
- tb4_hand_gesture/robot_behavior_node.py: ROS subscriber, timer, watchdog, Twist.
- config/gesture.yaml: ngưỡng, timeout và vận tốc/quãng đường/bán kính.
- launch/simulation.launch.py, gesture.launch.py: simulator riêng và hai node.
- scripts/setup_gesture_venv.sh, build.sh: môi trường cô lập và build.
- test/test_gesture_filter.py, test_behavior.py: kiểm tra logic và dừng.
- README.md, docs/DEMO.md, report/: hướng dẫn và báo cáo sau thực nghiệm.

Đường dẫn module Python ở trên nằm dưới src/tb4_hand_gesture/.

## Milestone 0 — Inspect

- [x] Kiểm tra Ubuntu, ROS và package simulator đã cài.
- [x] Đọc launch simulator và cấu hình đường cmd_vel.
- [x] Kiểm tra OpenCV, MediaPipe, camera và ROS graph.
- [x] Ghi kết quả thực tế trong docs/INSPECT.md.
- [x] Kiểm chứng đường cmd_vel và undock khi simulator chạy: hoàn thành ở Milestone 1.

## Milestone 1 — Simulation and webcam

- [x] Kiểm tra dependency MediaPipe/NumPy/OpenCV trong venv riêng; import cùng rclpy trước khi chốt version.
- [x] Tạo package và launch dùng simulator đã cài, tắt navigation/localization/SLAM theo launch thực tế.
- [x] Build bằng colcon; kiểm tra --show-args và prefix package mới.
- [x] Khởi động simulator; kiểm tra subscriber /cmd_vel, /odom, action /undock và nguồn vận tốc khác.
- [x] Undock hoàn tất, thử vận tốc thấp có thời hạn và zero Twist; quan sát robot thực sự di chuyển/dừng.
- [x] Đọc webcam ổn định; thử chuyển động ngắn sau undock. Kiểm tra khu vực cho hành vi dài còn lại ở M4.

## Milestone 2 — Recognition

- [x] Viết test gesture_filter trước: nhiễu ngắn không kích hoạt, Wave cần đảo hướng, tay đứng yên không là Wave.
- [x] Implement 5 nhãn MediaPipe + Wave theo landmark, dùng thời gian thực và ngưỡng cấu hình.
- [x] Publish std_msgs/String: WAVE, POINTING_UP, VICTORY, THUMB_UP, OPEN_PALM, CLOSED_FIST, NO_HAND, UNKNOWN.
- [x] Publish kết quả mới ở nhịp đều khi frame được xử lý; camera lỗi không lặp lại nhãn cũ.
- [ ] Test camera thực: đủ 6 cử chỉ, overlay nhãn/confidence, mất tay và hai tay. Wave hiển thị là suy ra chuyển động, không gán confidence AI giả.

## Milestone 3 — Behavior state machine

- [x] Test trước: select chưa chạy; confirm một lần; confirm khi chưa chọn không chạy.
- [x] Test Open_Palm/Closed_Fist ở mọi trạng thái, mất heartbeat, NO_HAND và dữ liệu không hợp lệ.
- [x] Implement IDLE/SELECTED/EXECUTING; stop/hủy xóa kế hoạch và cần chọn lại.
- [x] Timer không blocking; lệnh dừng publish zero ngay; timeout dùng monotonic time.
- [x] Chạy test pure Python và ROS topic test; đo thời gian dừng thực tế so với timeout cấu hình.

## Milestone 4 — Robot motions

- [x] Test profile chào, 4 cặp tiến–lùi, một vòng tròn, hoàn thành sinh zero Twist.
- [x] Implement profile có giới hạn; cấu hình tốc độ/khoảng cách/bán kính theo khu vực thực tế.
- [x] Kiểm chứng Gazebo + odom: đủ chu kỳ, vòng tròn, chào và ngắt giữa hành vi.
- [x] Xác nhận controller có timeout nếu behavior node chết. Không tuyên bố tránh vật cản tự động.

## Milestone 5 — Integration

- [ ] Demo bằng cử chỉ: giữ confirm, đổi nhanh, Wave/Open_Palm, mất tay, lỗi camera, dừng node recognition.
- [ ] Thử pause/reset simulation; không tiếp tục chuyển động bất ngờ.
- [ ] Ghi PASS/FAIL, log, tham số và thời gian dừng đo được; sửa lỗi rồi chạy lại case liên quan.

## Milestone 6 — Submission

- [ ] README cài/build/chạy đã xác minh, launch và YAML.
- [ ] Kịch bản video đủ 6 cử chỉ, chọn/xác nhận, dừng/hủy/mất tín hiệu.
- [ ] Báo cáo LaTeX: kiến trúc, node/topic, mapping, nhận diện tĩnh/động, kết quả thật, ảnh và link.
- [ ] GitHub public theo repo người dùng cung cấp; không đưa venv/build/log hoặc secret.

Sau mỗi milestone báo file thay đổi, lệnh build/chạy, test thực tế, lỗi và bước kế tiếp.
