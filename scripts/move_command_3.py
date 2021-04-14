#!/usr/bin/env python3

import rospy
import math
from tf.transformations import euler_from_quaternion, quaternion_from_euler
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry 

max_lin_vel = 0.22
max_ang_vel = 2.84

avg_speed = 0
speed_sum = 0
collisions = 0
counter = 0
is_collided = False
wall_dist = 0.4
turn_right = False
target_rad = 0
roll = pitch = yaw = 0.0



def callback(msg):
    global collisions, is_collided, max_ang_vel, max_lin_vel, wall_dist, counter, turn_right, target_rad
    #Fuld hastighed
    vel.linear.x = max_lin_vel
    vel.angular.z = 0

    #angles
    middle = 0
    f_right = 330
    f_left = 30
    left = 90
    right = 270
    
    middle_dist = msg.ranges[middle]
    f_right_dist = msg.ranges[f_right]
    f_left_dist = msg.ranges[f_left]
    right_dist = msg.ranges[right]
    left_dist = msg.ranges[left]

    #if middle_dist < 0.5:
        #vel.linear.x = map_range(middle_dist, 0.2, 0.5, 0, max_lin_vel)
        #turn left

    
    #print(yaw)

    if turn_right:
        vel.angular.z = 1 * (target_rad-yaw)
        
        if abs(target_rad-yaw) < 0.1:
            turn_right = False
        print_and_pub()
        return
    
    
    
        

    #keep in middle
    dist_diff = right_dist - left_dist
    vel.angular.z = map_range(dist_diff, -0.2, 0.2, 0.2, -0.2)
    print(dist_diff)
    if dist_diff > 0.5 and not turn_right:
        target_rad = -90*math.pi/180 + yaw
        turn_right = True
    
    print_and_pub()
    

def print_and_pub():
    global avg_speed, speed_sum, collisions, counter, is_collided
    counter += 1
    speed_sum += vel.linear.x
    avg_speed = speed_sum / counter
    #print("ang", "{:.2f}".format(vel.angular.z), "lin","{:.2f}".format(vel.linear.x), "col", collisions, "avg_vel", "{:.2f}".format(avg_speed))
    pub.publish(vel)
    
def get_yaw(msg):
    global roll, pitch, yaw
    orientation_q = msg.pose.pose.orientation
    orientation_list = [orientation_q.x, orientation_q.y, orientation_q.z, orientation_q.w]
    (roll, pitch, yaw) = euler_from_quaternion (orientation_list)

def map_range(value, start1, stop1, start2, stop2):
    return (value - start1) / (stop1 - start1) * (stop2 - start2) + start2

def shutdown():
    #print collisions og avg speed
    pub.publish(Twist())
    rospy.sleep(1)

rospy.on_shutdown(shutdown)

rospy.init_node('move_command')
rate = rospy.Rate(10) # 10hz
sub = rospy.Subscriber('scan', LaserScan, callback)
sub2 = rospy.Subscriber('/odom', Odometry, get_yaw)
pub = rospy.Publisher('cmd_vel', Twist, queue_size=10)
vel = Twist()


try:
    while not rospy.is_shutdown():


        rospy.spin()
except rospy.ROSInterruptException:
    print("Closing Node")


    
