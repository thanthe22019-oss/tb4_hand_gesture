"""Webcam gesture recognition only; never publishes robot velocity."""
import math
import signal
from pathlib import Path
import time

import cv2
import mediapipe as mp
from mediapipe.tasks.python import BaseOptions, vision
import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from std_msgs.msg import String

from tb4_hand_gesture.gesture_filter import GestureFilter, is_open_hand, palm_orientation

# Hand skeleton without depending on the legacy mediapipe.solutions API.
CONNECTIONS = [(0,1),(1,2),(2,3),(3,4),(0,5),(5,6),(6,7),(7,8),
               (5,9),(9,10),(10,11),(11,12),(9,13),(13,14),(14,15),
               (15,16),(13,17),(17,18),(18,19),(19,20),(0,17)]


class GestureRecognitionNode(Node):
    def __init__(self):
        super().__init__('gesture_recognition_node')
        defaults = {
            'camera_index': 0, 'width': 640, 'height': 480, 'rate_hz': 20.0,
            'show_window': True, 'mirror': True, 'model_path': '',
            'hold_seconds': .3, 'confidence_threshold': .75, 'stop_confidence': .6,
            'thumb_confidence': .55,
            'wave_window': 1.2, 'wave_amplitude': .5, 'wave_angle_amplitude': .35,
            'wave_idle_seconds': .2, 'max_frame_gap': .25, 'wave_label_grace': .25,
        }
        for key, value in defaults.items():
            self.declare_parameter(key, value)
        value = lambda key: self.get_parameter(key).value
        self.filter = GestureFilter(**{key: value(key) for key in [
            'hold_seconds', 'confidence_threshold', 'stop_confidence', 'thumb_confidence',
            'wave_window', 'wave_amplitude', 'wave_idle_seconds', 'max_frame_gap', 'wave_label_grace', 'wave_angle_amplitude']})
        rate = value('rate_hz')
        if not math.isfinite(rate) or not 1 <= rate <= 60:
            raise ValueError('rate_hz must be in [1, 60]')
        if value('width') <= 0 or value('height') <= 0:
            raise ValueError('Camera dimensions must be positive')
        model = Path(value('model_path')).expanduser()
        if not model.is_file():
            raise ValueError('model_path must name gesture_recognizer.task; run scripts/run_gesture.sh')
        self.show_window = value('show_window')
        self.mirror = value('mirror')
        self.publisher = self.create_publisher(String, '/detected_gesture', 1)
        self.camera = None
        self.recognizer = None
        self.window = 'TurtleBot 4 - Gestures'
        self.frames = 0
        self.started = time.monotonic()
        self.last_timestamp = -1
        self.last_label = None
        try:
            options = vision.GestureRecognizerOptions(
                base_options=BaseOptions(model_asset_path=str(model)),
                running_mode=vision.RunningMode.VIDEO, num_hands=2,
                min_hand_detection_confidence=.5,
                min_hand_presence_confidence=.5,
                min_tracking_confidence=.5)
            self.recognizer = vision.GestureRecognizer.create_from_options(options)
            self.camera = cv2.VideoCapture(value('camera_index'), cv2.CAP_V4L2)
            if not self.camera.isOpened():
                raise RuntimeError(f"Cannot open /dev/video{value('camera_index')}")
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, value('width'))
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, value('height'))
            self.camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            if self.show_window:
                cv2.namedWindow(self.window, cv2.WINDOW_NORMAL)
            self.timer = self.create_timer(1.0 / rate, self.process_frame)
            self.get_logger().info('Recognition ready; publishes /detected_gesture only. Q: close webcam.')
        except Exception:
            self.close()
            raise

    def publish(self, label):
        self.publisher.publish(String(data=label))
        if label != self.last_label:
            self.get_logger().info(f'Gesture: {label}')
            self.last_label = label

    def process_frame(self):
        frame_started = time.monotonic()
        ok, frame = self.camera.read()
        if not ok:
            self.publish('NO_HAND')
            raise RuntimeError('Camera lost: stopping recognition heartbeat')
        if self.mirror:
            frame = cv2.flip(frame, 1)
        now = time.monotonic()
        timestamp = max(self.last_timestamp + 1, int(now * 1000))
        self.last_timestamp = timestamp
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = self.recognizer.recognize_for_video(
            mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb), timestamp)
        count = len(result.hand_landmarks)
        open_hand = None
        angle = None
        raw, confidence, palm, size, hand = 'None', 0., (0., 0.), 1., ''
        if count == 1:
            points = result.hand_landmarks[0]
            if result.gestures and result.gestures[0]:
                raw = result.gestures[0][0].category_name
                confidence = float(result.gestures[0][0].score)
            if result.handedness and result.handedness[0]:
                hand = result.handedness[0][0].category_name
            aspect = frame.shape[0] / frame.shape[1]
            planar_points = [(p.x, p.y*aspect) for p in points]
            open_hand = is_open_hand(planar_points)
            angle = palm_orientation(planar_points)
            palm_points = [points[i] for i in [0, 5, 9, 13, 17]]
            palm = (sum(p.x for p in palm_points)/5,
                    sum(p.y for p in palm_points)/5 * aspect)
            size = math.hypot(points[5].x-points[17].x,
                              (points[5].y-points[17].y)*aspect)
        processed_at = time.monotonic()
        if processed_at-frame_started > self.filter.max_frame_gap:
            # A delayed image must not revive a previous command heartbeat.
            label = self.filter.update('None', 0., processed_at, palm, size, 2, hand)
        else:
            label = self.filter.update(raw, confidence, processed_at, palm, size, count, hand, open_hand=open_hand, palm_angle=angle)
        self.publish(label)
        self.frames += 1
        if self.show_window:
            self.draw(frame, result, label, raw, confidence, count)
            cv2.imshow(self.window, frame)
            if (cv2.waitKey(1) & 0xFF == ord('q') or
                    cv2.getWindowProperty(self.window, cv2.WND_PROP_VISIBLE) < 1):
                rclpy.try_shutdown()

    def draw(self, frame, result, label, raw, confidence, count):
        height, width = frame.shape[:2]
        for landmarks in result.hand_landmarks:
            pixels = [(int(p.x*width), int(p.y*height)) for p in landmarks]
            for a, b in CONNECTIONS:
                cv2.line(frame, pixels[a], pixels[b], (0, 200, 0), 2)
            for xy in pixels:
                cv2.circle(frame, xy, 3, (0, 200, 255), -1)
        text = f'{label} (temporal motion)' if label == 'WAVE' else label
        cv2.putText(frame, text, (12, 30), cv2.FONT_HERSHEY_SIMPLEX, .7, (0,255,0), 2)
        detail = f'AI: {raw} {confidence:.2f}' if count == 1 else f'Hands: {count}; no command'
        cv2.putText(frame, detail, (12, 60), cv2.FONT_HERSHEY_SIMPLEX, .6, (255,255,255), 2)
        cv2.putText(frame, 'Recognition only | Q: quit', (12, height-15),
                    cv2.FONT_HERSHEY_SIMPLEX, .55, (255,255,255), 1)

    def close(self):
        if self.camera is not None:
            self.camera.release()
        if self.recognizer is not None:
            self.recognizer.close()
        if self.show_window:
            cv2.destroyAllWindows()


def main(args=None):
    rclpy.init(args=args)
    node = None
    failed = False
    try:
        node = GestureRecognitionNode()
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    except Exception as error:
        failed = True
        if node is not None:
            if rclpy.ok():
                node.publish('NO_HAND')
            node.get_logger().error(str(error))
        else:
            print(f'Recognition initialization failed: {error}', flush=True)
    finally:
        # Terminal SIGINT and launch forwarding may arrive separately.
        # Finish releasing webcam/model even if another Ctrl+C arrives.
        previous_handler = signal.signal(signal.SIGINT, signal.SIG_IGN)
        try:
            if node is not None:
                if rclpy.ok():
                    node.publish('NO_HAND')
                node.close()
                elapsed = time.monotonic()-node.started
                print(f'Recognition processed {node.frames} frames in {elapsed:.2f} s',flush=True)
                node.destroy_node()
            rclpy.try_shutdown()
        finally:
            signal.signal(signal.SIGINT, previous_handler)
    if failed:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
