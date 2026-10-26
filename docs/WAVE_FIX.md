# Sửa nhận diện Wave khi vẫy nhanh — 25/10/2026

## Nguyên nhân được xác định từ code và tái hiện

Bộ lọc cũ xóa toàn bộ lịch sử khi gặp một frame None/confidence thấp. Chuỗi Open_Palm, None xen kẽ không tích lũy được hai lần đổi hướng.
Cùng chuỗi tọa độ mô phỏng, bản cũ kết thúc OPEN_PALM; bản sửa kết thúc WAVE. Đây là test hồi quy bằng dữ liệu tổng hợp, không phải số đo accuracy bằng camera.

## Thay đổi

- gesture_filter.py: thêm is_open_hand (ít nhất 3 ngón duỗi) và wave_label_grace=0,25 s.
- Cần có Open_Palm tin cậy gần đây trước khi dùng landmark để bù mất nhãn; geometry đơn lẻ không tự khởi tạo Wave.
- Các frame không rõ nhãn nhưng có bàn tay mở được tiếp tục cung cấp tọa độ trong thời hạn grace.
- Mất tay, nhiều tay, đổi tay hoặc frame gap vẫn xóa lịch sử. Closed_Fist hủy ngay.
- Kiểm tra biên độ chuyển động trong khoảng gần nhất; rung nhỏ không duy trì Wave sau khi ngừng vẫy.
- Node chuyển landmark theo cùng hệ đơn vị aspect-corrected trước khi kiểm tra ngón duỗi.
- YAML thêm wave_label_grace, không hạ ngưỡng stop/confirm chung.

## Bằng chứng kiểm thử

- Bổ sung test tái hiện mất nhãn ngắn, confidence thấp, geometry đơn lẻ, mất nhãn kéo dài, mất tay thật, nhiều tay, đứng yên, nắm tay và ngón duỗi.
- Test rung nhẹ sau Wave từng FAIL (vẫn WAVE); sửa rồi PASS (OPEN_PALM).
- Tổng cộng 24 unittest PASS. Build package PASS. Compile Python PASS.
- Runtime webcam GUI + ROS subscriber: nhận 235 bản tin, phân bố {'UNKNOWN': 4, 'NO_HAND': 231}; node không publish /cmd_vel.
- Khoảng nhận bản tin lớn nhất trong lần probe: 0.0819 giây; dữ liệu trong wave_fix_runtime.json.
- Probe webcam không có người thực hiện đủ chuỗi vẫy nhanh. Cần người dùng thử lại động tác thực tế; không khẳng định đã đo độ chính xác Wave.

## Chạy lại

Đóng phiên nhận diện cũ bằng Ctrl+C, chạy:

```bash
cd ~/Interaction/tb4_hand_gesture
./scripts/run_gesture.sh
```

Khi xòe tay đứng yên phải về OPEN_PALM. Khi vẫy ngang đủ hai lần đổi hướng phải có WAVE; khi mất landmark thật, UNKNOWN/NO_HAND vẫn là kết quả đúng theo cơ chế dừng.
Không commit/push.
