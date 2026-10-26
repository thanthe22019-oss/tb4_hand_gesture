# Progress — 2026-10-25-hand-gesture

Milestone 0: complete; xem INSPECT.md.
Milestone 1: complete. Build + show-args + imports + model inference + webcam GUI/headless + undock + bounded motion/zero stop verified. Evidence: MILESTONE_1.md and milestone1_motion.json.
Milestone 2: implementation + automated/runtime checks complete; six-gesture human acceptance pending. RED observed missing module, GREEN 13 tests. See MILESTONE_2.md and milestone2_runtime.json.
Ruling: dùng folder mới độc lập, chưa khởi tạo Git/commit theo yêu cầu người dùng; không cần worktree của repo cũ.
Ruling: dùng simulator warehouse đã cài cho M1; xác định khu vực trống từ dữ liệu runtime trước thử chuyển động dài ở M4.
Ruling: M1 chỉ scaffolding/launch/dependency và webcam probe; kiểm tra bằng build, --show-args, import, camera thật và robot runtime. Test máy trạng thái bắt đầu M2/M3.
Ruling: MediaPipe 0.10.32 thay 0.10.21; metadata PyPI xác nhận không cần JAX/JAXLIB, giảm dependency không dùng. Chốt sau import + model smoke test.
Ruling: Wave là chuyển động theo thời gian, không gán confidence AI cho nhãn Wave. Dừng/hủy không chờ hold 0,3s. Frame xử lý chậm >0,25s phát UNKNOWN, không làm mới lệnh cũ.
Ruling: Không tuyên bố đã nhận đúng 6 cử chỉ thật khi webcam probe chưa có người biểu diễn; ghi rõ bước nghiệm thu trực tiếp.
Wave regression: fixed brief classifier dropouts with tracked open-hand geometry and 0,25s grace. Fixed jitter sustaining Wave. 24 tests pass; runtime evidence WAVE_FIX.md; fast-wave human retest pending.
User approved minimal option 1: angular + translational Wave landmarks. Added 8 tests, total 32 PASS; static mapping unchanged. See WAVE_ANGULAR.md. Human Wave retest pending.
User confirmed Wave works in real test. Milestone 3 implementation: 17 behavior tests + 32 gesture tests PASS. Preview-only behavior node publishes zero velocity; physical motion remains M4.
Milestone 3 complete: 49 tests PASS, isolated ROS topic/state/watchdog test PASS, preview guard PASS. Physical profiles remain M4. See MILESTONE_3.md and milestone3_runtime.json.
Milestone 4 complete: 57 tests, odometry-fault ROS tests, three Gazebo profiles and physical stop/controller watchdog PASS. See MILESTONE_4.md. Full webcam-driven demo remains M5.

2026-10-26: Người dùng xác nhận điều khiển bằng cử chỉ đã thực hiện được sau khi thử lại. Chưa xác định đủ cả ba profile và mọi tình huống dừng qua webcam; không đánh dấu toàn bộ M5 hoàn thành. Log trước đó cho thấy một lần EXECUTING bị UNKNOWN hủy sau khoảng 0,398 giây. Chưa sửa logic nhận diện/dừng. Chuẩn bị checklist M5 tại MILESTONE_5_CHECKLIST.md.

2026-10-26: Người dùng xác nhận checklist M5 mục 1–9 đạt; yêu cầu bỏ qua 10–12 (chưa kiểm thử, không phải PASS). Tăng tốc qua behavior.yaml: linear_speed 0.08→0.12 m/s, angular_speed 0.35→0.45 rad/s. Các giới hạn hình học và watchdog giữ nguyên. Cấu hình tốc độ mới cần nghiệm thu Gazebo riêng.

2026-10-26: Người dùng xác nhận mọi hành vi sau tăng tốc đạt. M5 mục 10–12 vẫn bỏ qua. Chuẩn bị M6: README cập nhật, docs/DEMO.md, report/main.tex và ZIP Prism. Ảnh/họ tên/link thật chờ bổ sung; chưa compile PDF do thiếu XeLaTeX. Chưa commit/push.

2026-10-26: Đã kiểm tra trực quan và chèn 6 ảnh từ ảnh tuần 6.zip vào báo cáo, bổ sung link video Drive người dùng cung cấp. Chú thích ảnh 2 đúng trạng thái UNKNOWN/0.54, ảnh 4 EXECUTING/0.62. ZIP Prism đóng gói lại có ảnh. Chưa xem nội dung video hoặc xác minh quyền chia sẻ; GitHub và họ tên còn chờ bổ sung.

2026-10-26: Người dùng yêu cầu tạo repo mới và push. Repo dự kiến https://github.com/thanthe22019-oss/tb4_hand_gesture; README và báo cáo cập nhật link. report/, build/, install/, log/, venv và model tải về không đưa vào Git.
