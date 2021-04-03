#!/usr/bin/env python

import rospy
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan

max_lin_vel = 0.22
max_ang_vel = 2.84

avg_speed = 0
speed_sum = 0
collisions = 0
counter = 0
is_collided = False

def callback(msg):
    global avg_speed, speed_sum, collisions, counter, is_collided
    vel.linear.x = max_lin_vel
    vel.angular.z = 0
    middle = 0
    right = 330
    left = 30
    middle_dist = (msg.ranges[middle] + msg.ranges[359] + msg.ranges[middle + 1]) / 3
    right_dist = (msg.ranges[right] + msg.ranges[right - 1] + msg.ranges[right + 1]) / 3
    left_dist = (msg.ranges[left] + msg.ranges[left - 1] + msg.ranges[left + 1]) / 3
    if middle_dist < 0.5:
        vel.linear.x = map_range(middle_dist, 0.2, 0.5, 0, max_lin_vel)
        #if left_dist < right_dist:
            #turn right
            #vel.angular.z = -1
        #else:
            #turn left
            #vel.angular.z = 1
    if right_dist < 0.5:
        #turn left
        vel.angular.z = map_range(right_dist, 0.1, 0.5, 3.14/2, 0.4)
    
    if left_dist < 0.5:
        #turn right
        vel.angular.z = -1 * map_range(left_dist, 0.1, 0.5, 3.14/2, 0.4)
        if left_dist > right_dist:
            vel.angular.z = map_range(right_dist, 0.1, 0.5, 3.14/2, 0.4)
    
    #else
        #full speed
        

    if middle_dist < 0.15 or left_dist < 0.15 or right_dist < 0.15:
        if is_collided == False:
            collisions += 1
        is_collided = True

    if middle_dist >= 0.2 and left_dist >= 0.2 and right_dist >= 0.2:
        is_collided = False
    
    if is_collided:
        vel.linear.x = -0.1
        if msg.ranges[180-30] > 0.5:
            #turn right
            vel.angular.z = 0.5
        elif msg.ranges[180+30] > 0.5:
            #turn left
            vel.angular.z = -0.5



    counter += 1
    speed_sum += vel.linear.x
    avg_speed = speed_sum / counter
    print("ang", vel.angular.z, "lin", vel.linear.x, "col", collisions, "avg_vel", round(avg_speed, 5))
    pub.publish(vel)

#Bruges ikke
def update_vel(lin_vel, ang_vel):
    vel.linear.x = lin_vel
    vel.angular.z = ang_vel
    pub.publish(vel)

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
pub = rospy.Publisher('cmd_vel', Twist, queue_size=10)
vel = Twist()


try:
    while not rospy.is_shutdown():

        rospy.spin()
except rospy.ROSInterruptException:
    print("Closing Node")
