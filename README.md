# TurtleBot 4 — Điều khiển bằng cử chỉ tay (Bài 6)

MSSV **23020730**. Workspace trên máy: `~/Interaction/tb4_hand_gesture`.
Webcam laptop + MediaPipe nhận cử chỉ; hai node ROS 2 giao tiếp qua `/detected_gesture` để điều khiển TurtleBot 4 mô phỏng qua `/cmd_vel`. Không cần Nav2 hoặc bản đồ.

## 1. Chuẩn bị và build

Máy hiện dùng Ubuntu 22.04, ROS 2 Humble, TurtleBot 4 Simulator/Ignition Fortress và webcam `/dev/video0`.

```bash
cd ~/Interaction/tb4_hand_gesture
./scripts/build.sh
./scripts/setup_gesture_venv.sh
```

MediaPipe/NumPy/OpenCV riêng trong `.venv-gesture`; script tải model chính thức vào `models/gesture_recognizer.task`, lưu nguồn/SHA-256 ở `models/metadata.json`. Không cài AI vào Python hệ thống.
Đóng các phiên nhận diện/behavior/simulator cũ trước khi mở phiên mới. Chỉ chạy một nguồn điều khiển robot.

## 2. Mở sân mô phỏng

Terminal 1:

```bash
cd ~/Interaction/tb4_hand_gesture
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch tb4_hand_gesture arena.launch.py
```

Sân phẳng 20×20 m, không có chướng ngại ngoài robot và dock. Launch tái sử dụng robot/controllers cài sẵn; không sửa `/opt/ros` hoặc dự án cũ. Đây là sân dành cho các quỹ đạo của bài, không phải hệ thống tự tránh vật cản.

## 3. Rời dock và chuẩn bị chạy lùi

Terminal 2:

```bash
source /opt/ros/humble/setup.bash
source ~/Interaction/tb4_hand_gesture/install/setup.bash
ros2 action send_goal /undock irobot_create_msgs/action/Undock '{}' --feedback
```

Chờ `SUCCEEDED`, `is_docked: false`. Sau đó cấu hình riêng cho sân mô phỏng trống:

```bash
ros2 param set /motion_control safety_override backup_only
```

Create 3 có giới hạn lùi; nếu không cấu hình, robot có thể báo `Reached backup limit` và không hoàn thành các chu kỳ. `backup_only` bỏ giới hạn lùi, giữ các giới hạn tốc độ và bảo vệ cliff phía trước. Thiết lập này phục vụ sân mô phỏng của bài. Tham khảo [Create 3 Safety](https://iroboteducation.github.io/create3_docs/api/safety/).

## 4. Nhận cử chỉ và chạy robot

Terminal 3:

```bash
cd ~/Interaction/tb4_hand_gesture
./scripts/run_interaction.sh preview_only:=false
```

Script mở webcam và behavior node. Tham số `preview_only:=false` bật chuyển động thật trong Gazebo. Chờ `/behavior_status` có `odometry_ready: true` trước khi chọn và xác nhận.

| Cử chỉ | Kết quả |
| --- | --- |
| Vẫy tay ngang hoặc lắc bàn tay nghiêng trái–phải | Chọn chào: quay trái 30°, quay phải 60°, quay trái 30° |
| Giơ một ngón trỏ | Chọn tiến 0,2 m rồi lùi 0,2 m, lặp 4 chu kỳ |
| Victory/chữ V | Chọn một vòng tròn bán kính 0,4 m |
| Thumbs Up/ngón cái hướng lên | Xác nhận hành vi đã chọn; giữ lâu không kích hoạt lặp |
| Open Palm/xòe tay đứng yên | Dừng và xóa lựa chọn |
| Closed Fist/nắm tay | Hủy và về chờ |

Robot chỉ chạy sau xác nhận. Giữ bàn tay ở tư thế nhận diện rõ trong suốt hành vi. Mất tay, nhiều tay hoặc UNKNOWN khi đang chạy làm hủy; cần chọn lại và xác nhận lại, không tự tiếp tục.
Khi chọn chào bằng Wave, chuyển sang Thumbs Up để xác nhận; giữ tay xòe đứng yên được hiểu là dừng.

Các chuyển động dùng odometry để kiểm tra quãng đường/góc; tốc độ mặc định 0,12 m/s, quay tối đa 0,45 rad/s. Mỗi đoạn có thời gian dừng ngắn trước khi đổi hướng. Tham số trong `src/tb4_hand_gesture/config/behavior.yaml`.

Mất heartbeat 0,6 giây hoặc odometry không cập nhật 0,5 giây sẽ hủy chuyển động. Header odometry lặp không được coi là dữ liệu mới. Behavior node dùng timer wall time và monotonic clock; giữ `use_sim_time: false` cho node này để watchdog hoạt động khi Gazebo pause. Các node simulator vẫn dùng simulation time.

## 5. Chỉ kiểm tra webcam/logic

Nhận diện riêng, không có behavior node:

```bash
cd ~/Interaction/tb4_hand_gesture
./scripts/run_gesture.sh
```

Hai node cùng chạy, chỉ preview logic và phát vận tốc zero:

```bash
./scripts/run_interaction.sh
```

Q hoặc Ctrl+C để đóng. Có thể thêm `show_window:=false` hoặc `camera_index:=0` vào script. Cửa sổ hiển thị nhãn, skeleton và confidence AI; Wave là kết quả chuyển động theo thời gian, không gán confidence AI giả.

Xem topic:

```bash
source /opt/ros/humble/setup.bash
source ~/Interaction/tb4_hand_gesture/install/setup.bash
ros2 topic echo /detected_gesture
ros2 topic echo /behavior_status
```

Chạy từng lệnh echo trong terminal riêng hoặc Ctrl+C trước khi đổi lệnh. `/behavior_status` là JSON trong std_msgs/String, gồm state, selected, execution_id, reason, preview_only, odometry_ready và segment_index.

## 6. Cấu trúc và kiểm chứng

- `gesture_recognition_node.py`: webcam, MediaPipe, overlay và topic.
- `gesture_filter.py`: lọc tư thế, nhận Wave qua chuyển động ngang/góc cổ tay.
- `behavior.py`: chọn/xác nhận/dừng/hủy/watchdog.
- `motion.py`: profile chào, tiến–lùi và vòng tròn dựa trên odometry.
- `robot_behavior_node.py`: ROS adapter và /cmd_vel.
- `launch/`, `config/`, `worlds/`: khởi chạy và sân mô phỏng.

Các module trên ở `src/tb4_hand_gesture/`. Bằng chứng kiểm thử nằm trong [docs/MILESTONE_4.md](docs/MILESTONE_4.md); ghi rõ phép thử dùng nhãn ROS tổng hợp và phần demo bằng tay thật còn lại.


## 7. Quay video và bài nộp

Xem [kịch bản video và ảnh](docs/DEMO.md). Báo cáo LaTeX ở `report/main.tex`; tải `report/TB4_Gesture_23020730_Prism.zip` lên Prism, chọn compiler XeLaTeX. Đã chèn đủ 6 ảnh và link video minh chứng; GitHub: [tb4_hand_gesture](https://github.com/thanthe22019-oss/tb4_hand_gesture).

Ngón cái dùng ngưỡng riêng 0,55 và giữ ổn định 0,3 giây; chọn hành vi dùng ngưỡng 0,75. Đây là điểm tin cậy mô hình, không phải tỷ lệ chính xác thực nghiệm.
Người dùng xác nhận kiểm thử tích hợp mục 1–9 đạt, sau đó xác nhận các hành vi với tốc độ mới đạt. Mục 10–12 được bỏ qua, chưa nghiệm thu qua webcam; không ghi là PASS.

Video demo: [Google Drive](https://drive.google.com/drive/folders/1qb2WV-yFDvG7Bsu-qNK-DS6D19J91tDo?usp=sharing).

Repository Public: [https://github.com/thanthe22019-oss/tb4_hand_gesture](https://github.com/thanthe22019-oss/tb4_hand_gesture).

Clone về đúng tên thư mục được dùng trong hướng dẫn:

```bash
cd ~/Interaction
git clone https://github.com/thanthe22019-oss/tb4_hand_gesture.git tb4_hand_gesture
```
