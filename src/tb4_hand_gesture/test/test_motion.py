import math
import unittest
from tb4_hand_gesture.motion import MotionConfig, MotionExecutor, Pose


class MotionTests(unittest.TestCase):
    def simulate(self, action, pose=None):
        pose=pose or Pose(0.,0.,0.)
        engine=MotionExecutor(action,pose,0.)
        phases=set(); largest_v=largest_w=0.
        for i in range(8000):
            now=i*.02
            v,w,done=engine.step(pose,now)
            largest_v=max(largest_v,abs(v));largest_w=max(largest_w,abs(w))
            phases.add(engine.segment_index)
            pose=Pose(pose.x+v*math.cos(pose.yaw)*.02,
                      pose.y+v*math.sin(pose.yaw)*.02,
                      math.atan2(math.sin(pose.yaw+w*.02),math.cos(pose.yaw+w*.02)))
            if done: return pose,engine,phases,largest_v,largest_w
        self.fail('Motion did not complete')

    def test_four_back_and_forth_cycles_complete_near_start(self):
        p,e,phases,v,w=self.simulate('back_and_forth')
        self.assertEqual(e.segment_index,8)
        self.assertLess(math.hypot(p.x,p.y),.02)
        self.assertEqual(len(phases),9)
        self.assertLessEqual(v,.08)

    def test_greeting_turns_left_right_and_returns_heading(self):
        p,e,_,v,w=self.simulate('greet')
        self.assertEqual(e.segment_index,3)
        self.assertLess(abs(p.yaw),.05)
        self.assertEqual(v,0.)
        self.assertLessEqual(w,.35)

    def test_circle_handles_yaw_wraparound(self):
        start=Pose(0.,0.,3.)
        p,e,_,v,w=self.simulate('circle',start)
        self.assertLess(math.hypot(p.x,p.y),.025)
        self.assertLess(abs(math.atan2(math.sin(p.yaw-start.yaw),math.cos(p.yaw-start.yaw))),.05)
        self.assertLessEqual(v,.08)

    def test_stuck_robot_times_out(self):
        e=MotionExecutor('back_and_forth',Pose(0,0,0),0.)
        with self.assertRaisesRegex(RuntimeError,'motion_timeout'):
            e.step(Pose(0,0,0),e.config.segment_timeout+1.)

    def test_no_motion_after_completion(self):
        p,e,_,_,_=self.simulate('greet')
        self.assertEqual(e.step(p,100.),(0.,0.,True))

    def test_bad_action_or_configuration_is_rejected(self):
        with self.assertRaises(ValueError): MotionExecutor('unknown',Pose(0,0,0),0.)
        for value in [0,-1,float('nan')]:
            with self.assertRaises(ValueError): MotionConfig(linear_speed=value)

    def test_invalid_pose_stops_with_error(self):
        e=MotionExecutor('greet',Pose(0,0,0),0.)
        with self.assertRaises(ValueError):e.step(Pose(0,0,float('nan')),.1)

    def test_distance_does_not_depend_on_global_heading(self):
        p,_,_,_,_=self.simulate('back_and_forth',Pose(1.,2.,2.))
        self.assertLess(math.hypot(p.x-1,p.y-2),.02)

if __name__=='__main__':unittest.main()
