"""Preview/test webcam only. Does not publish robot commands or save images."""
import argparse
import math
import time
import cv2


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--camera', type=int, default=0)
    parser.add_argument('--duration', type=float, default=0,
                        help='Seconds; zero means run until Q or Ctrl+C.')
    parser.add_argument('--headless', action='store_true')
    args = parser.parse_args()
    if not math.isfinite(args.duration) or args.duration < 0:
        parser.error('--duration must be finite and nonnegative')
    if args.headless and args.duration == 0:
        parser.error('--headless requires a positive --duration')
    camera = cv2.VideoCapture(args.camera, cv2.CAP_V4L2)
    frames = 0
    start = time.monotonic()
    try:
        if not camera.isOpened():
            raise RuntimeError(f'Cannot open /dev/video{args.camera}')
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        while args.duration == 0 or time.monotonic() - start < args.duration:
            ok, frame = camera.read()
            if not ok:
                raise RuntimeError('Camera stopped supplying frames')
            frames += 1
            if not args.headless:
                frame = cv2.flip(frame, 1)
                cv2.putText(frame, 'Webcam check | Q: quit', (15, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.imshow('TurtleBot 4 - Webcam', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
    except KeyboardInterrupt:
        pass
    finally:
        camera.release()
        if not args.headless:
            cv2.destroyAllWindows()
    if frames == 0:
        raise RuntimeError('No camera frames received')
    print(f'Camera OK: {frames} frames, {time.monotonic() - start:.2f} s')


if __name__ == '__main__':
    main()
