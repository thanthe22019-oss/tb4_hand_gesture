# Kịch bản quay video và chụp ảnh — Bài 6

MSSV: 23020730. Chạy trong ~/Interaction/tb4_hand_gesture.

## 1. Khởi chạy

Terminal 1:

```bash
cd ~/Interaction/tb4_hand_gesture
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch tb4_hand_gesture arena.launch.py
```

Terminal 2, đợi robot và action server sẵn sàng:

```bash
source /opt/ros/humble/setup.bash
source ~/Interaction/tb4_hand_gesture/install/setup.bash
ros2 action send_goal /undock irobot_create_msgs/action/Undock '{}' --feedback
```

Chờ SUCCEEDED và is_docked: false, rồi chạy:

```bash
ros2 param set /motion_control safety_override backup_only
```

Terminal 3:

```bash
cd ~/Interaction/tb4_hand_gesture
./scripts/run_interaction.sh preview_only:=false 2>&1 | tee /tmp/tb4_gesture_demo.log
```

Terminal 4 nếu cần quan sát trạng thái:

```bash
source /opt/ros/humble/setup.bash
ros2 topic echo /behavior_status
```

## 2. Quay video

Dùng trình ghi màn hình của Ubuntu (Ctrl+Alt+Shift+R nếu khả dụng) hoặc ứng dụng ghi màn hình bạn đang dùng. Sắp Gazebo cạnh cửa sổ webcam; phóng camera Gazebo để thấy toàn quỹ đạo. Terminal trạng thái có thể đặt ở cạnh dưới. Không dùng bàn phím điều khiển chuyển động trong phần demo; undock là bước chuẩn bị trước demo.

1. Giới thiệu Bài 6 và MSSV; cho thấy webcam có skeleton/nhãn.
2. Giơ 1 ngón và giữ: SELECTED, xe đứng yên. Sau đó giơ ngón cái và giữ rõ trong camera: xe tiến–lùi đủ 4 chu kỳ rồi dừng.
3. Giơ chữ V, xác nhận bằng ngón cái: xe đi một vòng bán kính 0,4 m rồi dừng.
4. Vẫy tay: xuất hiện WAVE và SELECTED greet; chuyển sang ngón cái để xe chào trái–phải. Không dừng ở bàn tay xòe tĩnh trước khi xác nhận vì đó là STOP.
5. Chọn/xác nhận một hành vi khác; xòe tay khi xe đang chạy để chứng minh dừng.
6. Chọn hoặc chạy lại, nắm tay để chứng minh hủy và về IDLE.
7. Chọn/xác nhận, đưa tay ra khỏi webcam: xe dừng. Đưa tay trở lại không tự tiếp tục. Chọn và xác nhận lại nếu muốn chạy.
8. Nếu cần minh chứng chống nhiễu: giữ ngón cái sau khi hoàn thành, xe không tự lặp; đưa hai tay vào thì không tiếp tục chuyển động.

Giữ toàn bàn tay trong ảnh, ánh sáng đủ; chuyển tư thế liên tục. UNKNOWN trong khi chạy sẽ hủy ngay. Video ghi kết quả thực tế, không cắt ghép để che lỗi và không nêu thời gian/tỷ lệ chưa đo.

## 3. Ảnh báo cáo

Dùng phím Print Screen hoặc công cụ Screenshot của Ubuntu, chọn vùng gồm cửa sổ cần chứng minh. Lưu PNG đúng tên dưới đây trong report/images/.

| Ảnh | Tên file | Cách chụp và nội dung cần thấy |
|---|---|---|
| 1 | 01_setup.png | Gazebo thấy robot trên sân, webcam hoạt động; không cần cho thấy bí mật/tài khoản |
| 2 | 02_recognition.png | Webcam thấy ngón cái, skeleton, nhãn THUMB_UP và confidence; chụp sau khi ổn định |
| 3 | 03_selection.png | Giơ 1 ngón, terminal SELECTED back_and_forth; xe chưa thực hiện trước xác nhận |
| 4 | 04_motion.png | Gazebo và webcam lúc EXECUTING; ảnh chỉ minh họa chuyển động, video chứng minh đủ chu kỳ/vòng |
| 5 | 05_wave.png | Vẫy tay để thấy nhãn WAVE; Wave là phân tích chuyển động, không có confidence phân loại riêng |
| 6 | 06_stop.png | Sau khi xòe tay, thấy OPEN_PALM và IDLE reason stop; xe đã dừng |

Có thể bổ sung ảnh nắm tay/hủy nếu muốn. Không dùng một ảnh tĩnh làm bằng chứng đủ 4 lần tiến–lùi.

## 4. Hoàn thiện bài nộp

- Thêm ảnh vào report/images/ rồi upload lại project trên Prism, compiler XeLaTeX.
- Sửa hai macro VideoURL và RepoURL ở đầu main.tex khi có link thật. Video Drive phải cho người có link xem; GitHub Public.
- Zip hiện tại chưa có ảnh thật hoặc link thật. Không đưa .venv-gesture, build, install, log, khóa API vào GitHub.
- Mục kiểm thử 10–12 bỏ qua theo yêu cầu, không ghi đạt. Các phép thử tự động trước đó không thay thế nghiệm thu webcam cho các mục này.
