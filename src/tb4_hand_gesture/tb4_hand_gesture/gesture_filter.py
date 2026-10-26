"""Temporal gesture filtering, independent of ROS, OpenCV and MediaPipe."""
from collections import deque
import math
from statistics import median


def is_open_hand(points):
    """Geometric support for a brief classifier dropout, not a gesture classifier.

    points contains 21 (x,y) landmarks in the same aspect-corrected units.
    At least three of four fingers must be straight and extend away from wrist.
    """
    if len(points) != 21 or not all(math.isfinite(v) for point in points for v in point):
        return False
    extended = 0
    wrist = points[0]
    for base in [5, 9, 13, 17]:
        start, joint, tip = points[base], points[base+1], points[base+3]
        a = (start[0]-joint[0], start[1]-joint[1])
        b = (tip[0]-joint[0], tip[1]-joint[1])
        denominator = math.hypot(*a)*math.hypot(*b)
        straight = denominator > 1e-8 and (a[0]*b[0]+a[1]*b[1])/denominator < -.766
        if straight and math.dist(tip, wrist) > 1.1*math.dist(joint, wrist):
            extended += 1
    return extended >= 3


def palm_orientation(points):
    """In-plane orientation of wrist -> middle MCP, upright palm = zero."""
    if len(points) != 21:
        return None
    dx = points[9][0]-points[0][0]
    dy = points[9][1]-points[0][1]
    if not math.isfinite(dx) or not math.isfinite(dy) or math.hypot(dx,dy) < 1e-8:
        return None
    return math.atan2(dx, -dy)


class GestureFilter:
    """Emit current gesture; confirmation edge handling belongs to behavior node."""

    LABELS = {'Pointing_Up': 'POINTING_UP', 'Victory': 'VICTORY',
              'Thumb_Up': 'THUMB_UP'}

    def __init__(self, hold_seconds=.3, confidence_threshold=.75,
                 stop_confidence=.6, wave_window=1.2, wave_amplitude=.5,
                 wave_idle_seconds=.2, max_frame_gap=.25, wave_label_grace=.25, wave_angle_amplitude=.35, thumb_confidence=.55):
        for value in [hold_seconds, wave_window, wave_amplitude,
                      wave_idle_seconds, max_frame_gap, wave_label_grace, wave_angle_amplitude]:
            if not math.isfinite(value) or value <= 0:
                raise ValueError('Temporal/geometry thresholds must be positive and finite')
        if not 0 <= stop_confidence <= confidence_threshold <= 1:
            raise ValueError('Require 0 <= stop_confidence <= confidence_threshold <= 1')
        if not math.isfinite(thumb_confidence) or not 0 <= thumb_confidence <= 1:
            raise ValueError("thumb_confidence must be in [0, 1]")
        self.thumb_confidence = thumb_confidence
        self.hold_seconds = hold_seconds
        self.confidence_threshold = confidence_threshold
        self.stop_confidence = stop_confidence
        self.wave_window = wave_window
        self.wave_amplitude = wave_amplitude
        self.wave_idle_seconds = wave_idle_seconds
        self.max_frame_gap = max_frame_gap
        self.wave_label_grace = wave_label_grace
        self.wave_angle_amplitude = wave_angle_amplitude
        self.last_time = None
        self._clear()

    def _clear(self):
        self.hand = None
        self.candidate = None
        self.candidate_since = None
        self._clear_wave()

    def _clear_wave(self):
        self.points = deque(maxlen=120)
        self.last_confident_palm = None
        self.smooth_palm = None
        self.smooth_angle = None
        self.motion_time = None

    def update(self, label, confidence, now, palm, hand_size, hands, hand, open_hand=None, palm_angle=None):
        """Coordinates and hand_size share units; now is monotonic seconds."""
        if not math.isfinite(now):
            self._clear()
            self.last_time = None
            return 'UNKNOWN'
        if self.last_time is not None:
            if now <= self.last_time:
                self._clear()
                self.last_time = now
                return 'UNKNOWN'
            if now - self.last_time > self.max_frame_gap:
                self._clear()
        self.last_time = now
        if hands == 0:
            self._clear()
            return 'NO_HAND'
        if (hands != 1 or not all(math.isfinite(v) for v in
                                 [confidence, *palm, hand_size]) or hand_size <= 0 or
                (palm_angle is not None and not math.isfinite(palm_angle))):
            self._clear()
            return 'UNKNOWN'
        if hand != self.hand:
            self._clear()
            self.hand = hand
        if not 0 <= confidence <= 1:
            self._clear()
            return 'UNKNOWN'
        if label == 'Closed_Fist' and confidence >= self.stop_confidence:
            self._clear_wave()
            self.last_confident_palm = None
            self.candidate = None
            self.candidate_since = None
            return 'CLOSED_FIST'
        confident_palm = label == 'Open_Palm' and confidence >= self.stop_confidence
        recent_palm = (self.last_confident_palm is not None and
                       now-self.last_confident_palm <= self.wave_label_grace)
        uncertain_palm = label in ['None', 'Open_Palm', None]
        supported_dropout = uncertain_palm and open_hand is True and recent_palm
        if confident_palm or supported_dropout:
            if confident_palm:
                self.last_confident_palm = now
            self.candidate = None
            self.candidate_since = None
            self._add_motion(now, palm, hand_size, palm_angle)
            while self.points and now-self.points[0][0] > self.wave_window:
                self.points.popleft()
            if self._is_wave(now):
                return 'WAVE'
            return 'OPEN_PALM' if confident_palm else 'UNKNOWN'
        if uncertain_palm:
            # Keep a short history, but never invent motion without landmarks.
            self.candidate = None
            self.candidate_since = None
            if not recent_palm:
                self._clear_wave()
                self.last_confident_palm = None
            return 'UNKNOWN'
        self._clear_wave()
        self.last_confident_palm = None
        threshold = self.thumb_confidence if label == "Thumb_Up" else self.confidence_threshold
        if label not in self.LABELS or confidence < threshold:
            self._clear()
            return 'UNKNOWN'
        if self.candidate != label:
            self.candidate = label
            self.candidate_since = now
        if now - self.candidate_since >= self.hold_seconds:
            return self.LABELS[label]
        return 'UNKNOWN'

    def _add_motion(self, now, palm, size, angle):
        # Short time-based EMA smooths landmarks, never static gesture labels.
        alpha = 1. if self.motion_time is None else 1.-math.exp(-(now-self.motion_time)/.03)
        if self.smooth_palm is None:
            self.smooth_palm = palm
        else:
            self.smooth_palm = tuple(old+alpha*(new-old) for old,new in zip(self.smooth_palm,palm))
        if angle is None or self.smooth_angle is None:
            self.smooth_angle = angle
        else:
            # Unwrap +/-pi before filtering so wraparound cannot fake reversals.
            delta = math.atan2(math.sin(angle-self.smooth_angle), math.cos(angle-self.smooth_angle))
            self.smooth_angle += alpha*delta
        self.motion_time = now
        self.points.append((now, *self.smooth_palm, size, self.smooth_angle))

    def _is_wave(self, now):
        if len(self.points) < 4:
            return False
        scale = median(p[3] for p in self.points)
        if max(p[2] for p in self.points)-min(p[2] for p in self.points) > .8*scale:
            return False
        translation = [(p[0],p[1]) for p in self.points]
        rotation = [(p[0],p[4]) for p in self.points if p[4] is not None]
        return (self._oscillates(translation, self.wave_amplitude*scale, now) or
                self._oscillates(rotation, self.wave_angle_amplitude, now))

    def _oscillates(self, samples, amplitude, now):
        if len(samples) < 4:
            return False
        direction = 0
        reversals = 0
        extreme = samples[0][1]
        for _,value in samples:
            if direction == 0:
                if abs(value-extreme) >= amplitude:
                    direction = 1 if value > extreme else -1
                    extreme = value
            elif direction > 0:
                if value > extreme:
                    extreme = value
                elif extreme-value >= amplitude:
                    reversals += 1
                    direction = -1
                    extreme = value
            else:
                if value < extreme:
                    extreme = value
                elif value-extreme >= amplitude:
                    reversals += 1
                    direction = 1
                    extreme = value
        recent = [value for stamp,value in samples if now-stamp <= self.wave_idle_seconds]
        moving = len(recent) >= 2 and max(recent)-min(recent) >= .3*amplitude
        return reversals >= 2 and moving
