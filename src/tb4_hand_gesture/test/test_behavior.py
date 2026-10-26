import unittest
from tb4_hand_gesture.behavior import BehaviorController


class BehaviorTests(unittest.TestCase):
    def setUp(self):
        self.c = BehaviorController(heartbeat_timeout=.6, selection_timeout=5.)

    def select_and_confirm(self):
        self.c.receive('POINTING_UP', 0.)
        self.c.receive('THUMB_UP', .1)

    def test_selection_does_not_execute(self):
        for gesture, action in [('WAVE','greet'),('POINTING_UP','back_and_forth'),('VICTORY','circle')]:
            c=BehaviorController()
            c.receive(gesture,0.)
            self.assertEqual(c.state,'SELECTED')
            self.assertEqual(c.selected,action)
            self.assertEqual(c.execution_id,0)

    def test_confirm_without_selection_does_nothing(self):
        self.c.receive('THUMB_UP',0.)
        self.assertEqual(self.c.state,'IDLE')
        self.assertEqual(self.c.execution_id,0)

    def test_confirm_executes_once_while_held(self):
        self.select_and_confirm()
        for t in [.2,.3,.4,.5]:
            self.c.receive('THUMB_UP',t)
        self.assertEqual(self.c.state,'EXECUTING')
        self.assertEqual(self.c.execution_id,1)

    def test_selected_gesture_can_be_changed_before_confirmation(self):
        self.c.receive('POINTING_UP',0.)
        self.c.receive('VICTORY',.1)
        self.c.receive('THUMB_UP',.2)
        self.assertEqual(self.c.selected,'circle')
        self.assertEqual(self.c.execution_id,1)

    def test_selection_during_execution_does_not_replace_action(self):
        self.select_and_confirm()
        self.c.receive('VICTORY',.2)
        self.assertEqual(self.c.selected,'back_and_forth')
        self.assertEqual(self.c.execution_id,1)

    def test_stop_and_cancel_clear_all_states(self):
        for gesture in ['OPEN_PALM','CLOSED_FIST','NO_HAND']:
            for state in ['IDLE','SELECTED','EXECUTING']:
                c=BehaviorController()
                if state != 'IDLE': c.receive('VICTORY',0.)
                if state == 'EXECUTING': c.receive('THUMB_UP',.1)
                c.receive(gesture,.2)
                self.assertEqual(c.state,'IDLE')
                self.assertIsNone(c.selected)

    def test_unknown_during_confirmation_transition_preserves_selection(self):
        self.c.receive('VICTORY',0.)
        self.c.receive('UNKNOWN',.1)
        self.c.receive('UNKNOWN',.3)
        self.c.receive('THUMB_UP',.4)
        self.assertEqual(self.c.state,'EXECUTING')

    def test_unknown_during_execution_stops_without_auto_resume(self):
        self.select_and_confirm()
        self.c.receive('UNKNOWN',.2)
        self.c.receive('THUMB_UP',.3)
        self.assertEqual(self.c.state,'IDLE')
        self.assertIsNone(self.c.selected)
        self.assertEqual(self.c.execution_id,1)

    def test_watchdog_deadline_cancels_execution(self):
        self.select_and_confirm()
        self.c.tick(.699)
        self.assertEqual(self.c.state,'EXECUTING')
        self.c.tick(.701)
        self.assertEqual(self.c.state,'IDLE')
        self.assertEqual(self.c.reason,'heartbeat_timeout')

    def test_fresh_message_does_not_revive_stale_selection(self):
        self.c.receive('VICTORY',0.)
        self.c.receive('THUMB_UP',.7)
        self.assertEqual(self.c.state,'IDLE')
        self.assertEqual(self.c.execution_id,0)

    def test_no_hand_requires_selection_again(self):
        self.select_and_confirm()
        self.c.receive('NO_HAND',.2)
        self.c.receive('THUMB_UP',.3)
        self.assertEqual(self.c.state,'IDLE')
        self.c.receive('VICTORY',.4)
        self.c.receive('THUMB_UP',.5)
        self.assertEqual(self.c.execution_id,2)

    def test_completion_clears_action_and_held_thumb_cannot_repeat(self):
        self.select_and_confirm()
        self.c.complete(.2)
        self.c.receive('THUMB_UP',.3)
        self.assertEqual(self.c.state,'IDLE')
        self.assertEqual(self.c.execution_id,1)

    def test_uncertain_frames_cannot_keep_selection_forever(self):
        self.c.receive('VICTORY',0.)
        for i in range(1,52): self.c.receive('UNKNOWN',i*.1)
        self.assertEqual(self.c.state,'IDLE')
        self.assertEqual(self.c.reason,'selection_timeout')

    def test_held_selection_is_still_current(self):
        for i in range(70): self.c.receive('VICTORY',i*.1)
        self.assertEqual(self.c.state,'SELECTED')
        self.c.receive('THUMB_UP',7.)
        self.assertEqual(self.c.state,'EXECUTING')

    def test_invalid_messages_cancel_execution(self):
        for bad in ['', 'go', 'thumb_up', None, 4]:
            c=BehaviorController()
            c.receive('VICTORY',0.)
            c.receive('THUMB_UP',.1)
            c.receive(bad,.2)
            self.assertEqual(c.state,'IDLE')
            self.assertEqual(c.reason,'invalid_gesture')

    def test_invalid_or_backward_time_cancels_execution(self):
        for bad in [float('nan'),float('inf'),-.1]:
            c=BehaviorController()
            c.receive('VICTORY',0.)
            c.receive('THUMB_UP',.1)
            c.tick(bad)
            self.assertEqual(c.state,'IDLE')
            self.assertIsNone(c.selected)

    def test_invalid_timeouts_rejected(self):
        for bad in [0,-1,float('nan'),float('inf')]:
            with self.assertRaises(ValueError): BehaviorController(heartbeat_timeout=bad)


if __name__ == '__main__':
    unittest.main()
