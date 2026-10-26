"""Bounded odometry-feedback profiles. No ROS or camera dependencies."""
from dataclasses import dataclass
import math


def wrap(angle):
    return math.atan2(math.sin(angle),math.cos(angle))


@dataclass(frozen=True)
class Pose:
    x: float
    y: float
    yaw: float


@dataclass(frozen=True)
class MotionConfig:
    linear_speed: float = .08
    angular_speed: float = .35
    travel_distance: float = .2
    circle_radius: float = .4
    greet_angle: float = math.pi/6
    distance_tolerance: float = .008
    angle_tolerance: float = .025
    settle_seconds: float = .4
    segment_timeout: float = 60.

    def __post_init__(self):
        if any(not math.isfinite(v) or v <= 0 for v in vars(self).values()):
            raise ValueError('Motion parameters must be positive and finite')
        if self.linear_speed > .2 or self.angular_speed > .6:
            raise ValueError('Gesture demo speed limits: linear <= 0.2 m/s, angular <= 0.6 rad/s')
        if self.travel_distance <= self.distance_tolerance or self.greet_angle <= self.angle_tolerance:
            raise ValueError('Targets must exceed stopping tolerance')


class MotionExecutor:
    def __init__(self, action, pose, now, config=None):
        self.config = config or MotionConfig()
        c=self.config
        profiles={'greet':[('turn',c.greet_angle),('turn',-2*c.greet_angle),('turn',c.greet_angle)],
                  'back_and_forth':[('line',c.travel_distance),('line',-c.travel_distance)]*4,
                  'circle':[('circle',2*math.pi)]}
        if action not in profiles: raise ValueError('Unknown motion action')
        self.segments=profiles[action]
        self.segment_index=0
        self.start_pose=pose
        self.previous_yaw=pose.yaw
        self.turn_progress=0.
        self.segment_started=now
        self.settle_until=None

    def step(self, pose, now):
        if not all(math.isfinite(v) for v in [pose.x,pose.y,pose.yaw,now]):
            raise ValueError('Invalid odometry')
        if self.segment_index >= len(self.segments): return 0.,0.,True
        if now-self.segment_started > self.config.segment_timeout:
            raise RuntimeError('motion_timeout')
        self.turn_progress += wrap(pose.yaw-self.previous_yaw)
        self.previous_yaw=pose.yaw
        if self.settle_until is not None:
            if now >= self.settle_until:
                self.segment_index+=1
                self.start_pose=pose
                self.turn_progress=0.
                self.segment_started=now
                self.settle_until=None
            return 0.,0.,self.segment_index>=len(self.segments)
        kind,target=self.segments[self.segment_index]
        c=self.config
        if kind=='line':
            remaining=abs(target)-math.hypot(pose.x-self.start_pose.x,pose.y-self.start_pose.y)
            if remaining > c.distance_tolerance:
                v=math.copysign(min(c.linear_speed,max(.025,remaining)),target)
                w=max(-.2,min(.2,1.5*wrap(self.start_pose.yaw-pose.yaw)))
                return v,w,False
        else:
            remaining=abs(target)-math.copysign(1.,target)*self.turn_progress
            if remaining > c.angle_tolerance:
                limit=min(c.angular_speed,c.linear_speed/c.circle_radius) if kind=='circle' else c.angular_speed
                w=math.copysign(min(limit,max(.08,remaining)),target)
                return (c.circle_radius*w if kind=='circle' else 0.),w,False
        self.settle_until=now+c.settle_seconds
        return 0.,0.,False
