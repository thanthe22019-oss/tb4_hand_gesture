# Milestone 5 — Kiểm thử tích hợp bằng webcam

## Trạng thái

Người dùng đã xác nhận robot thực hiện được điều khiển bằng cử chỉ. Các mục dưới đây cần kiểm tra riêng; chưa coi là PASS khi chưa có kết quả.
Không thay đổi ngưỡng nhận diện hoặc logic dừng ở bước chuẩn bị này.

## Chuẩn bị

- Chỉ chạy một arena.launch.py và một interaction.launch.py.
- Không chạy teleop/Nav2 đồng thời.
- Robot đã undock thành công; safety_override là backup_only trong sân mô phỏng.
- Chạy interaction với preview_only:=false.
- Đặt webcam đủ sáng, toàn bàn tay trong ảnh. Khi xác nhận, tiếp tục giữ ngón cái rõ trong camera.
- UNKNOWN khi đang chạy sẽ hủy; NO_HAND, OPEN_PALM và CLOSED_FIST xóa lựa chọn. Sau hủy phải chọn và xác nhận lại.

Ghi log khi mở interaction:

```bash
cd ~/Interaction/tb4_hand_gesture
./scripts/run_interaction.sh preview_only:=false 2>&1 | tee /tmp/tb4_gesture_integration.log
```

## Checklist — cập nhật theo xác nhận người dùng ngày 26/10/2026

| ID | Thao tác | Kết quả mong đợi | Kết quả thực tế |
|---|---|---|---|
| 1 | Giơ 1 ngón, chưa xác nhận | SELECTED, robot đứng yên | Đạt theo xác nhận người dùng (cấu hình tốc độ cũ) |
| 2 | Chuyển sang ngón cái và giữ | EXECUTING, tiến–lùi đủ 4 chu kỳ, kết thúc IDLE | Đạt theo xác nhận người dùng (cấu hình tốc độ cũ) |
| 3 | Giơ 2 ngón, xác nhận và giữ | Robot đi một vòng tròn rồi dừng | Đạt theo xác nhận người dùng (cấu hình tốc độ cũ) |
| 4 | Vẫy tay, chuyển sang xác nhận | Chọn greet, xác nhận mới xoay trái–phải | Đạt theo xác nhận người dùng (cấu hình tốc độ cũ) |
| 5 | Xòe tay khi đang chạy | Dừng, IDLE với reason stop | Đạt theo xác nhận người dùng (cấu hình tốc độ cũ) |
| 6 | Nắm tay sau khi chọn hoặc khi chạy | Hủy, IDLE với reason cancel | Đạt theo xác nhận người dùng (cấu hình tốc độ cũ) |
| 7 | Đưa tay khỏi ảnh khi chạy | Dừng, reason no_hand; đưa tay lại không tự chạy | Đạt theo xác nhận người dùng (cấu hình tốc độ cũ) |
| 8 | Giữ ngón cái sau khi hành vi kết thúc | Không tự lặp lại hành vi | Đạt theo xác nhận người dùng (cấu hình tốc độ cũ) |
| 9 | Đưa hai tay vào ảnh | Không tiếp tục chạy với tín hiệu mơ hồ | Đạt theo xác nhận người dùng (cấu hình tốc độ cũ) |
| 10 | Dừng node nhận diện trong lúc chạy | Behavior watchdog dừng robot | Bỏ qua theo yêu cầu; chưa kiểm thử |
| 11 | Tạm dừng Gazebo trong lúc chạy rồi bật lại | Không tự tiếp tục hành vi cũ sau watchdog | Bỏ qua theo yêu cầu; chưa kiểm thử |
| 12 | Reset mô phỏng | Odom lỗi/reset hoặc mất tín hiệu ngăn hành vi cũ tiếp tục | Bỏ qua theo yêu cầu; chưa kiểm thử |

Vẫy tay có thể chuyển về OPEN_PALM và hủy lựa chọn nếu giữ bàn tay xòe tĩnh quá lâu trước khi xác nhận. Theo dõi SELECTED trên terminal khi chuyển tư thế.
Không rút webcam tích hợp laptop; trường hợp lỗi camera cần thử riêng bằng camera USB hoặc phương thức kiểm thử có kiểm soát.

## Minh chứng cần lưu

- Cửa sổ webcam với nhãn cử chỉ và độ tin cậy cho các cử chỉ tĩnh; Wave là nhận diện chuyển động theo thời gian.
- Gazebo thấy robot chào, tiến–lùi và đi vòng tròn.
- Terminal thấy SELECTED → EXECUTING → completed; dừng/hủy có reason tương ứng.
- Chỉ ghi thời gian dừng nếu có đo; không dùng thời gian của test tự động làm số đo webcam.

## Bước tiếp theo

Hoàn thành checklist và sửa các lỗi tái hiện được. Sau đó chuẩn bị kịch bản video, ảnh và báo cáo ở Milestone 6. Chưa commit/push.

## Tăng tốc sau nghiệm thu

Tốc độ cấu hình tăng từ 0,08 lên 0,12 m/s; tốc độ góc tối đa từ 0,35 lên 0,45 rad/s. Giữ quãng tiến/lùi 0,2 m, bán kính 0,4 m và mọi điều kiện dừng. Cần thử lại trên Gazebo với tốc độ mới; kết quả nghiệm thu 1–9 ở trên là trước thay đổi này.
