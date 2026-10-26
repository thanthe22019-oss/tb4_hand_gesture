#!/usr/bin/env bash
set -eo pipefail
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source /opt/ros/humble/setup.bash
cd "$PROJECT_DIR"
/usr/bin/colcon build --base-paths src --packages-select tb4_hand_gesture --symlink-install
