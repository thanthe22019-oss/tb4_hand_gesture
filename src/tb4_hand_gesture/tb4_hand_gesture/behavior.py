"""Gesture selection/confirmation state machine, independent of ROS and motion."""
import math


class BehaviorController:
    ACTIONS = {'WAVE': 'greet', 'POINTING_UP': 'back_and_forth', 'VICTORY': 'circle'}
    VALID = set(ACTIONS) | {'THUMB_UP','OPEN_PALM','CLOSED_FIST','NO_HAND','UNKNOWN'}

    def __init__(self, heartbeat_timeout=.6, selection_timeout=5.):
        for value in [heartbeat_timeout, selection_timeout]:
            if not math.isfinite(value) or value <= 0:
                raise ValueError('Timeouts must be finite and positive')
        self.heartbeat_timeout = heartbeat_timeout
        self.selection_timeout = selection_timeout
        self.state = 'IDLE'
        self.selected = None
        self.execution_id = 0
        self.reason = 'startup'
        self.last_time = None
        self.last_message = None
        self.selected_since = None

    def _stop(self, reason):
        self.state = 'IDLE'
        self.selected = None
        self.selected_since = None
        self.reason = reason

    def tick(self, now):
        if not math.isfinite(now) or (self.last_time is not None and now < self.last_time):
            self._stop('invalid_time')
            self.last_time = None
            self.last_message = None
            return False
        self.last_time = now
        if self.state != 'IDLE' and self.last_message is not None:
            if now-self.last_message >= self.heartbeat_timeout:
                self._stop('heartbeat_timeout')
            elif self.state == 'SELECTED' and now-self.selected_since >= self.selection_timeout:
                self._stop('selection_timeout')
        return True

    def receive(self, gesture, now):
        if not self.tick(now):
            return
        if not isinstance(gesture,str) or gesture not in self.VALID:
            self._stop('invalid_gesture')
            return
        self.last_message = now
        if gesture in ['OPEN_PALM','CLOSED_FIST','NO_HAND']:
            self._stop({'OPEN_PALM':'stop','CLOSED_FIST':'cancel','NO_HAND':'no_hand'}[gesture])
        elif gesture == 'UNKNOWN':
            # Selection can survive the brief transition into a confirming pose.
            # Uncertainty during execution always stops; it never auto-resumes.
            if self.state == 'EXECUTING':
                self._stop('uncertain_gesture')
        elif gesture in self.ACTIONS:
            if self.state != 'EXECUTING':
                self.state = 'SELECTED'
                self.selected = self.ACTIONS[gesture]
                self.selected_since = now
                self.reason = 'selected'
        elif gesture == 'THUMB_UP' and self.state == 'SELECTED':
            self.state = 'EXECUTING'
            self.execution_id += 1
            self.reason = 'confirmed'

    def complete(self, now):
        if self.tick(now) and self.state == 'EXECUTING':
            self._stop('completed')

    def cancel(self, reason):
        self._stop(reason)

    def snapshot(self):
        return {'state':self.state, 'selected':self.selected,
                'execution_id':self.execution_id, 'reason':self.reason}
