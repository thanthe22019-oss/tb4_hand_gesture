import unittest
from tb4_hand_gesture.gesture_filter import GestureFilter, is_open_hand


class GestureFilterTests(unittest.TestCase):
    def setUp(self):
        self.f = GestureFilter()

    def observe(self, label, t, x=.5, y=.5, size=.15, score=.95,
                hands=1, hand='Right', open_hand=None):
        return self.f.update(label, score, t, (x, y), size, hands, hand, open_hand=open_hand)

    def test_selection_and_confirmation_require_stability(self):
        for raw, expected in [('Pointing_Up','POINTING_UP'),
                              ('Victory','VICTORY'), ('Thumb_Up','THUMB_UP')]:
            self.f = GestureFilter()
            self.assertEqual(self.observe(raw, 0), 'UNKNOWN')
            self.assertEqual(self.observe(raw, .15), 'UNKNOWN')
            self.assertEqual(self.observe(raw, .31), expected)

    def test_thumb_at_sixty_percent_requires_hold(self):
        self.assertEqual(self.observe('Thumb_Up', 0, score=.60), 'UNKNOWN')
        self.assertEqual(self.observe('Thumb_Up', .15, score=.60), 'UNKNOWN')
        self.assertEqual(self.observe('Thumb_Up', .31, score=.60), 'THUMB_UP')
        self.assertEqual(self.observe('Thumb_Up', .4, score=.50), 'UNKNOWN')

    def test_other_selection_thresholds_stay_strict(self):
        for raw in ['Pointing_Up', 'Victory']:
            self.f = GestureFilter()
            for t in [0, .15, .31]:
                self.assertEqual(self.observe(raw, t, score=.60), 'UNKNOWN')

    def test_short_noise_does_not_select(self):
        self.observe('Victory', 0)
        self.observe('Pointing_Up', .1)
        self.assertEqual(self.observe('Victory', .2), 'UNKNOWN')

    def test_stop_and_cancel_are_immediate(self):
        self.assertEqual(self.observe('Open_Palm', 0, score=.65), 'OPEN_PALM')
        self.assertEqual(self.observe('Closed_Fist', .1, score=.65), 'CLOSED_FIST')

    def test_low_confidence_is_unknown(self):
        for t in [0, .15, .31]:
            self.assertEqual(self.observe('Thumb_Up', t, score=.5), 'UNKNOWN')
        self.assertEqual(self.observe('Open_Palm', .4, score=.5), 'UNKNOWN')

    def test_static_palm_and_small_jitter_are_not_wave(self):
        for i in range(40):
            result=self.observe('Open_Palm', i*.05, x=.5+(.003 if i%2 else -.003))
            self.assertEqual(result,'OPEN_PALM')

    def test_one_way_motion_is_not_wave(self):
        for i in range(15):
            self.assertEqual(self.observe('Open_Palm', i*.05, x=.2+i*.015), 'OPEN_PALM')

    def wave(self, y=.5):
        result=None
        for i,x in enumerate([.4,.46,.52,.46,.4,.46,.52]):
            result=self.observe('Open_Palm', i*.1, x=x, y=y)
        return result

    def test_wave_needs_two_reversals(self):
        self.assertEqual(self.wave(),'WAVE')

    def test_stationary_palm_after_wave_returns_stop(self):
        self.wave()
        self.observe('Open_Palm', .7, x=.52)
        self.assertEqual(self.observe('Open_Palm', .85, x=.52),'OPEN_PALM')

    def test_no_hand_clears_wave_and_confirmation(self):
        self.wave()
        self.assertEqual(self.observe('Open_Palm', .7, hands=0),'NO_HAND')
        self.assertEqual(self.observe('Open_Palm', .8, x=.4),'OPEN_PALM')
        self.assertEqual(self.observe('Thumb_Up', .9),'UNKNOWN')

    def test_multiple_hands_clear_history(self):
        self.wave()
        self.assertEqual(self.observe('Thumb_Up', .7, hands=2),'UNKNOWN')
        self.assertEqual(self.observe('Thumb_Up', .8),'UNKNOWN')

    def test_hand_change_or_frame_gap_clears_confirmation(self):
        self.observe('Thumb_Up',0)
        self.observe('Thumb_Up',.15)
        self.assertEqual(self.observe('Thumb_Up',.31,hand='Left'),'UNKNOWN')
        self.assertEqual(self.observe('Thumb_Up',.8,hand='Left'),'UNKNOWN')

    def test_invalid_observation_does_not_confirm(self):
        for args in [dict(score=float('nan')),dict(x=float('nan')),dict(size=0)]:
            self.assertEqual(self.observe('Thumb_Up',0,**args),'UNKNOWN')
        self.assertEqual(self.observe('None',.1),'UNKNOWN')

    def test_large_vertical_motion_rejects_wave(self):
        for i,x in enumerate([.4,.46,.52,.46,.4,.46,.52]):
            result=self.observe('Open_Palm',i*.1,x=x,y=.2+i*.035)
        self.assertEqual(result,'OPEN_PALM')

    def test_fast_wave_survives_brief_classifier_dropouts(self):
        labels = ['Open_Palm', 'None', 'Open_Palm', 'None',
                  'Open_Palm', 'None', 'Open_Palm']
        for i, (x, raw) in enumerate(zip([.4,.46,.52,.46,.4,.46,.52], labels)):
            result = self.observe(raw, i*.06, x=x,
                                  score=.95 if raw == 'Open_Palm' else .2,
                                  open_hand=True)
        self.assertEqual(result, 'WAVE')

    def test_fast_wave_low_palm_confidence_uses_recent_open_hand_evidence(self):
        for i,x in enumerate([.4,.46,.52,.46,.4,.46,.52]):
            result = self.observe('Open_Palm', i*.05, x=x,
                                  score=.95 if i%2 == 0 else .4,
                                  open_hand=True)
        self.assertEqual(result, 'WAVE')

    def test_geometry_alone_cannot_start_wave(self):
        for i,x in enumerate([.4,.46,.52,.46,.4,.46,.52]):
            result=self.observe('None',i*.05,x=x,score=.1,open_hand=True)
        self.assertEqual(result,'UNKNOWN')

    def test_unknown_without_open_landmarks_never_emits_wave(self):
        self.wave()
        self.assertEqual(self.observe('None', .65, x=.46, score=.1, open_hand=False), 'UNKNOWN')

    def test_lost_classifier_beyond_grace_resets_wave(self):
        self.observe('Open_Palm',0,x=.4,open_hand=True)
        for i,x in enumerate([.46,.52,.46,.4,.46,.52],start=1):
            result=self.observe('None',i*.1,x=x,score=.1,open_hand=True)
        self.assertEqual(result,'UNKNOWN')
        self.assertEqual(self.observe('Open_Palm',.7,x=.4,open_hand=True),'OPEN_PALM')

    def test_real_hand_loss_not_hidden_by_classifier_grace(self):
        self.wave()
        self.assertEqual(self.observe('None',.65,hands=0,open_hand=True),'NO_HAND')
        self.assertEqual(self.observe('Open_Palm',.7,x=.4,open_hand=True),'OPEN_PALM')

    def test_multiple_hands_not_hidden_by_classifier_grace(self):
        self.wave()
        self.assertEqual(self.observe('None',.65,hands=2,open_hand=True),'UNKNOWN')
        self.assertEqual(self.observe('Open_Palm',.7,x=.4,open_hand=True),'OPEN_PALM')

    def test_stationary_uncertain_hand_does_not_extend_wave(self):
        self.wave()
        for t in [.7,.8,.9]:
            result=self.observe('None',t,x=.52,score=.1,open_hand=True)
        self.assertEqual(result,'UNKNOWN')

    def test_fist_still_immediately_cancels_wave(self):
        self.wave()
        self.assertEqual(self.observe('Closed_Fist',.65,score=.65,open_hand=False),'CLOSED_FIST')

    def test_open_landmark_geometry_requires_three_extended_fingers(self):
        points=[(.5,.9)]*21
        for base in [5,9,13,17]:
            x=.2+base*.02
            points[base:base+4]=[(x,.65),(x,.45),(x,.3),(x,.15)]
        self.assertTrue(is_open_hand(points))
        for base in [5,9]:
            points[base+3]=(points[base][0],.7)
        self.assertFalse(is_open_hand(points))
        self.assertFalse(is_open_hand([]))
        self.assertFalse(is_open_hand([(float('nan'),0)]*21))

    def test_small_jitter_after_wave_does_not_keep_wave_active(self):
        self.wave()
        for i in range(1,7):
            result=self.observe('Open_Palm',.6+i*.05,x=.52+(.003 if i%2 else -.003))
        self.assertEqual(result,'OPEN_PALM')

    def angle_observe(self, angle, t, x=.5, hand='Right', hands=1):
        return self.f.update('Open_Palm', .95, t, (x,.5), .15, hands, hand,
                             open_hand=True, palm_angle=angle)

    def angle_wave(self):
        for i,angle in enumerate([-.4,-.1,.4,.1,-.4,-.1,.4]):
            result=self.angle_observe(angle,i*.1)
        return result

    def test_wave_by_wrist_rotation_without_center_translation(self):
        self.assertEqual(self.angle_wave(),'WAVE')

    def test_stationary_or_small_angular_jitter_is_not_wave(self):
        for i in range(25):
            self.assertEqual(self.angle_observe(.4+(.015 if i%2 else -.015),i*.05),'OPEN_PALM')

    def test_rotation_one_direction_is_not_wave(self):
        for i in range(15):
            self.assertEqual(self.angle_observe(-.8+i*.12,i*.05),'OPEN_PALM')

    def test_angle_wraparound_is_not_false_wave(self):
        for i in range(20):
            self.assertEqual(self.angle_observe(3.13 if i%2 else -3.13,i*.05),'OPEN_PALM')

    def test_rotation_stops_without_latching_wave(self):
        self.angle_wave()
        self.angle_observe(.4,.7)
        self.assertEqual(self.angle_observe(.4,.85),'OPEN_PALM')

    def test_rotation_history_clears_when_hand_disappears(self):
        self.angle_wave()
        self.assertEqual(self.angle_observe(.4,.65,hands=0),'NO_HAND')
        self.assertEqual(self.angle_observe(-.4,.7),'OPEN_PALM')

    def test_nonfinite_angle_is_rejected(self):
        self.assertEqual(self.angle_observe(float('nan'),0),'UNKNOWN')

    def test_palm_angle_is_computed_from_wrist_and_middle_knuckle(self):
        from tb4_hand_gesture.gesture_filter import palm_orientation
        points=[(.5,.5)]*21
        points[9]=(.5,.3)
        self.assertAlmostEqual(palm_orientation(points),0)
        points[9]=(.7,.5)
        self.assertAlmostEqual(palm_orientation(points),1.57079632679)
        self.assertIsNone(palm_orientation([]))
        points[9]=points[0]
        self.assertIsNone(palm_orientation(points))

if __name__ == '__main__':
    unittest.main()
