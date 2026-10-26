# Milestone 2 — Nhận diện và ROS topic

## Đã triển khai

- gesture_filter.py: lọc cử chỉ theo thời gian, nhận Wave từ lịch sử tâm bàn tay theo kích thước bàn tay, không phụ thuộc ROS/MediaPipe.
- gesture_recognition_node.py: OpenCV + MediaPipe VIDEO, tối đa 2 tay để phát hiện trường hợp nhiều tay; overlay skeleton, nhãn và confidence.
- Topic /detected_gesture, std_msgs/msg/String, queue depth 1, volatile; phát từ frame mới. Không phát vận tốc.
- Gesture YAML, recognition.launch.py và scripts/run_gesture.sh dùng đúng interpreter venv.
- Dừng/hủy không chờ hold; frame cũ/chậm không làm mới lệnh trước.

## Kiểm thử thực tế

- RED: test lỗi do chưa có module gesture_filter; sau implementation, 13 test PASS.
- Test bao gồm 3 tư thế chọn/xác nhận, dừng/hủy tức thời, nhiễu, thiếu confidence, jitter, chuyển một hướng, Wave hai lần đổi hướng, chuyển đứng yên về stop, nhiều tay/mất tay, đổi tay, frame gap và input không hợp lệ.
- Build package và launch --show-args: PASS.
- Chạy launch nhận diện với webcam GUI và subscriber ROS 18 giây: nhận 234 bản tin; nhãn {'UNKNOWN': 1, 'NO_HAND': 233}.
- Khoảng cách bản tin nhận lớn nhất trong lần chạy: 0.0818 giây. Đây chỉ là phép đo lần chạy này, không phải cam kết latency hay accuracy.
- Publisher topic: gesture_recognition_node. Kiểm tra graph xác nhận node không publish /cmd_vel.
- Camera và inference hoạt động trên frame webcam; chưa có người thực hiện đủ 6 cử chỉ trước camera trong phép thử tự động.

## Lỗi tìm thấy và sửa

Ctrl+C gửi vào cả launch/process group và launch còn forward SIGINT, khiến lần SIGINT thứ hai ngắt camera.release. Bảo vệ giai đoạn cleanup khỏi SIGINT lặp; kiểm tra lại bằng launch thật và webcam: process exit 0, không còn traceback khi tắt.

- Model không tồn tại và camera index không tồn tại: cả hai thoát mã 1 với thông báo rõ ràng.

## Kiểm tra trực tiếp còn cần người dùng

1. Lần lượt thử 5 tư thế tĩnh, kiểm tra nhãn/confidence trên cửa sổ và topic.
2. Vẫy tay ngang đủ hai lần đổi hướng, xác nhận WAVE; ngừng vẫy và giữ xòe tay phải về OPEN_PALM.
3. Thử hai tay, che tay hoặc đưa ra khỏi camera: UNKNOWN/NO_HAND.
4. Thử ánh sáng/khoảng cách thực tế để chỉnh ngưỡng nếu cần. Chưa có accuracy hoặc confusion matrix thực nghiệm.

## Lệnh và bước tiếp

Xem README.md: ./scripts/build.sh, ./scripts/run_gesture.sh, ros2 topic echo /detected_gesture.
Milestone 3: robot_behavior_node và máy trạng thái chọn/xác nhận/dừng/hủy/watchdog. Chưa có hành vi robot ở M2.
Không commit/push.
