#!/usr/bin/env bash
set -eo pipefail
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source /opt/ros/humble/setup.bash
# System pip remains readable; all installs target this virtual environment.
if [[ ! -x "$PROJECT_DIR/.venv-gesture/bin/python" ]]; then
  /usr/bin/python3 -m venv --without-pip --system-site-packages "$PROJECT_DIR/.venv-gesture"
fi
"$PROJECT_DIR/.venv-gesture/bin/python" -m pip install -r "$PROJECT_DIR/requirements-gesture.txt"
"$PROJECT_DIR/.venv-gesture/bin/python" - <<'CHECK'
import sys, cv2, numpy, mediapipe, rclpy
from mediapipe.tasks.python import vision
from cv_bridge import CvBridge
assert sys.prefix != sys.base_prefix
print('Python:', sys.executable)
print('MediaPipe:', mediapipe.__version__)
print('NumPy:', numpy.__version__, 'OpenCV:', cv2.__version__)
print('GestureRecognizer:', vision.GestureRecognizer.__name__)
print('rclpy:', rclpy.__file__, 'cv_bridge:', CvBridge.__name__)
CHECK

# Download the official model without touching the old project.
"$PROJECT_DIR/.venv-gesture/bin/python" - "$PROJECT_DIR" <<'MODEL'
import hashlib, json, sys, urllib.request
from pathlib import Path
folder = Path(sys.argv[1]) / 'models'
folder.mkdir(exist_ok=True)
model = folder / 'gesture_recognizer.task'
url = 'https://storage.googleapis.com/mediapipe-models/gesture_recognizer/gesture_recognizer/float16/1/gesture_recognizer.task'
if not model.exists():
    temporary = folder / 'gesture_recognizer.task.part'
    try:
        with urllib.request.urlopen(url, timeout=60) as response, temporary.open('wb') as output:
            import shutil
            shutil.copyfileobj(response, output)
        temporary.replace(model)
    finally:
        temporary.unlink(missing_ok=True)
metadata = {'source': url, 'sha256': hashlib.sha256(model.read_bytes()).hexdigest(), 'bytes': model.stat().st_size}
(folder / 'metadata.json').write_text(json.dumps(metadata, indent=2) + '\n')
from mediapipe.tasks.python import BaseOptions, vision
with vision.GestureRecognizer.create_from_options(vision.GestureRecognizerOptions(base_options=BaseOptions(model_asset_path=str(model)))):
    print('Official Gesture Recognizer model loaded:', model)
MODEL
