"""Gesture state machine and bounded odometry-feedback motion profiles."""
import json
import math
import signal
import time

import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from std_msgs.msg import String
from tb4_hand_gesture.behavior import BehaviorController
from tb4_hand_gesture.motion import MotionConfig, MotionExecutor, Pose, wrap


class RobotBehaviorNode(Node):
    def __init__(self):
        super().__init__('robot_behavior_node')
        defaults={'heartbeat_timeout':.6,'selection_timeout':5.,'rate_hz':20.,
                  'preview_only':True,'odom_timeout':.5,**vars(MotionConfig())}
        for key,default in defaults.items():self.declare_parameter(key,default)
        value=lambda name:self.get_parameter(name).value
        self.preview=value('preview_only')
        self.controller=BehaviorController(value('heartbeat_timeout'),value('selection_timeout'))
        self.config=MotionConfig(**{name:value(name) for name in vars(MotionConfig())})
        self.odom_timeout=value('odom_timeout')
        if not math.isfinite(self.odom_timeout) or self.odom_timeout<=0:
            raise ValueError('odom_timeout must be finite and positive')
        rate=value('rate_hz')
        if not math.isfinite(rate) or not 1<=rate<=100 or 1/rate>self.controller.heartbeat_timeout/2:
            raise ValueError('rate_hz must be in [1,100] and timer period <= heartbeat_timeout/2')
        # Keep this node on wall/monotonic time so watchdog still runs when Gazebo pauses.
        if self.get_parameter('use_sim_time').value:
            raise ValueError('behavior node must use use_sim_time=false for its watchdog timer')
        self.velocity=self.create_publisher(Twist,'/cmd_vel',1)
        self.status=self.create_publisher(String,'/behavior_status',1)
        self.subscriber=self.create_subscription(String,'/detected_gesture',self.on_gesture,1)
        self.odometry=self.create_subscription(Odometry,'/odom',self.on_odometry,qos_profile_sensor_data)
        self.pose=None;self.pose_received=None;self.pose_stamp=None
        self.motion=None;self.motion_id=None;self.last_status=None
        self.timer=self.create_timer(1/rate,self.on_timer)
        self.get_logger().info('PREVIEW: zero velocities only' if self.preview else 'MOTION ENABLED: confirmation + fresh odometry required')
        self.publish_outputs()

    def on_odometry(self,message):
        p=message.pose.pose.position;q=message.pose.pose.orientation
        values=[p.x,p.y,q.x,q.y,q.z,q.w]
        norm=sum(v*v for v in [q.x,q.y,q.z,q.w])
        if not all(math.isfinite(v) for v in values) or norm<1e-8:
            self.pose=None
            self.controller.cancel('invalid_odometry')
            self.publish_outputs();return
        scale=math.sqrt(norm)
        x,y,z,w=[v/scale for v in [q.x,q.y,q.z,q.w]]
        pose=Pose(p.x,p.y,math.atan2(2*(w*z+x*y),1-2*(y*y+z*z)))
        stamp=message.header.stamp.sec+message.header.stamp.nanosec*1e-9
        # Repeated cached odometry must not refresh the motion watchdog.
        if self.pose_stamp is not None and stamp==self.pose_stamp:
            return
        reset=self.pose_stamp is not None and stamp<self.pose_stamp-1e-6
        jump=self.pose is not None and (math.hypot(pose.x-self.pose.x,pose.y-self.pose.y)>.5 or abs(wrap(pose.yaw-self.pose.yaw))>1.)
        if reset or jump:
            self.controller.cancel('odom_reset' if reset else 'odom_jump')
            self.motion=None
        self.pose=pose;self.pose_received=time.monotonic();self.pose_stamp=stamp
        if reset or jump:self.publish_outputs()

    def on_gesture(self,message):
        self.controller.receive(message.data,time.monotonic())
        self.publish_outputs()

    def on_timer(self):
        self.controller.tick(time.monotonic())
        self.publish_outputs()

    def publish_outputs(self):
        now=time.monotonic();v=w=0.
        if not self.preview and self.controller.state=='EXECUTING':
            if self.pose is None or now-self.pose_received>=self.odom_timeout:
                self.controller.cancel('odometry_unavailable')
            else:
                try:
                    if self.motion is None or self.motion_id!=self.controller.execution_id:
                        self.motion=MotionExecutor(self.controller.selected,self.pose,now,self.config)
                        self.motion_id=self.controller.execution_id
                    v,w,done=self.motion.step(self.pose,now)
                    if done:
                        self.controller.complete(now);v=w=0.
                except (ValueError,RuntimeError) as error:
                    self.controller.cancel(str(error));v=w=0.
        if self.controller.state!='EXECUTING':self.motion=None;v=w=0.
        command=Twist();command.linear.x=v;command.angular.z=w
        self.velocity.publish(command)
        snapshot=self.controller.snapshot()
        snapshot['preview_only']=self.preview
        snapshot['odometry_ready']=self.pose is not None and now-self.pose_received<self.odom_timeout
        snapshot['segment_index']=self.motion.segment_index if self.motion is not None else None
        self.status.publish(String(data=json.dumps(snapshot,separators=(',',':'))))
        identity=tuple(snapshot.values())
        if identity!=self.last_status:
            self.get_logger().info(str(snapshot));self.last_status=identity


def main(args=None):
    rclpy.init(args=args)
    node=None;failed=False
    try:
        node=RobotBehaviorNode();rclpy.spin(node)
    except (KeyboardInterrupt,ExternalShutdownException):pass
    except Exception as error:
        failed=True
        if node is not None:node.get_logger().error(str(error))
        else:print(f'Behavior initialization failed: {error}',flush=True)
    finally:
        previous=signal.signal(signal.SIGINT,signal.SIG_IGN)
        try:
            if node is not None:
                if rclpy.ok():
                    node.controller.receive('NO_HAND',time.monotonic());node.publish_outputs()
                node.destroy_node()
            rclpy.try_shutdown()
        finally:signal.signal(signal.SIGINT,previous)
    if failed:raise SystemExit(1)


if __name__=='__main__':main()
