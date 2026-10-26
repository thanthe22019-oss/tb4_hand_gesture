#!/usr/bin/env bash
set -eo pipefail
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ ! -x "$PROJECT_DIR/.venv-gesture/bin/python" || ! -f "$PROJECT_DIR/models/gesture_recognizer.task" ]]; then
  echo "Chạy ./scripts/setup_gesture_venv.sh trước." >&2
  exit 1
fi
if [[ ! -f "$PROJECT_DIR/install/setup.bash" ]]; then
  echo "Chạy ./scripts/build.sh trước." >&2
  exit 1
fi
source /opt/ros/humble/setup.bash
source "$PROJECT_DIR/install/setup.bash"
exec ros2 launch tb4_hand_gesture recognition.launch.py   python_executable:="$PROJECT_DIR/.venv-gesture/bin/python"   model_path:="$PROJECT_DIR/models/gesture_recognizer.task" "$@"
