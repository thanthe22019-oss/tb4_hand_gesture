# Wave bằng chuyển động ngang hoặc góc cổ tay — 25/10/2026

## Phạm vi người dùng đã chọn

Chỉ cải tiến cử chỉ động Wave theo phương án 1. Giữ nguyên nhận diện cử chỉ tĩnh, model MediaPipe, dependency và giao diện /detected_gesture. Không triển khai optical flow/YOLO/huấn luyện mới.

## Cách nhận

- Tâm bàn tay từ các landmark gốc ngón; chuẩn hóa biên độ theo trung vị kích thước bàn tay.
- Bổ sung góc hướng landmark cổ tay (0) đến gốc ngón giữa (9), aspect-corrected.
- EMA ngắn với hằng số thời gian 0,03 giây chỉ cho tọa độ/góc. Không làm mượt hoặc trì hoãn nhãn stop/cancel tĩnh.
- Đếm ít nhất hai lần đổi hướng đủ biên độ trong cửa sổ 1,2 giây; nhận được dịch ngang HOẶC lắc góc trong mặt phẳng ảnh.
- Ngưỡng góc mặc định wave_angle_amplitude=0,35 rad (~20 độ giữa cực trị), lưu YAML.
- Xử lý vòng góc +/-pi để không nhầm việc vượt biên thành vẫy.
- Có kiểm tra còn chuyển động gần đây, không giữ WAVE khi đứng yên/rung nhẹ.
- Giữ các điều kiện mất tay, nhiều tay, frame quá chậm, thiếu confidence và khoảng bù nhãn 0,25 giây của bản trước.

## Kiểm thử

RED trước implementation: 8 test mới lỗi do chưa có đầu vào góc/hàm hướng bàn tay.
GREEN: 32 test PASS, gồm 24 test hồi quy trước và 8 test góc mới.
Ca mới gồm: cổ tay lắc khi tâm tay đứng yên; góc tĩnh/rung nhẹ; xoay một chiều; vượt biên +/-pi; ngừng lắc về OPEN_PALM; mất tay xóa lịch sử; góc NaN; trích hướng từ landmark.
Build package và compile Python PASS.
Runtime: Webcam/ROS probe PASS; no human gesture accuracy measured.

Đây là kiểm thử logic + pipeline, chưa phải số đo độ chính xác trên lần vẫy thật của người dùng. Chưa khẳng định đã giải quyết mọi kiểu vẫy, nhất là khi ngón bị che hoặc ảnh nhòe đến mức mất landmark.

## File thay đổi

- gesture_filter.py: palm_orientation, kênh chuyển động góc, làm mượt và kiểm tra đổi hướng dùng chung cho Wave.
- gesture_recognition_node.py: lấy góc và truyền cho bộ nhận Wave.
- config/gesture.yaml: wave_angle_amplitude.
- test/test_gesture_filter.py: test góc và hồi quy.
- README.md, tài liệu và progress.

Các file Python/config/test ở dưới src/tb4_hand_gesture/.

## Thử trực tiếp

Đóng phiên cũ bằng Ctrl+C; chạy ./scripts/run_gesture.sh trong ~/Interaction/tb4_hand_gesture.
Xòe tay đứng yên: OPEN_PALM. Lắc nghiêng trái–phải hoặc dịch ngang đủ hai lần đổi hướng: WAVE. Nắm tay: CLOSED_FIST. Đưa tay khỏi khung hình: NO_HAND.
Khi mới bắt đầu chuyển động, OPEN_PALM/UNKNOWN có thể xuất hiện trước khi tích lũy đủ hai lần đổi hướng; không giữ nhãn Wave giả sau khi chuyển động kết thúc.
Chưa commit/push.
