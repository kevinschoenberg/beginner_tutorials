#!/usr/bin/env python3

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
    global collisions, is_collided, max_ang_vel, max_lin_vel
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

    if middle_dist < 0.5:
        vel.linear.x = map_range(middle_dist, 0.2, 0.5, 0, max_lin_vel)
        if middle_dist < 0.2:
            if right_dist < 1:
                if left_dist < 1:
                    #turn
                    vel.angular.z = map_range(middle_dist, 0.2, 0.5, 3, 0)
                else:
                    #turn left
                    vel.angular.z = 1.5
        else:
            #turn right
            vel.angular.z = -1.5
    elif right_dist > 1:
        #turn right
         vel.angular.z = -1.5
    elif left_dist > 1:
        #turn left
         vel.angular.z = 1.5

    if f_right_dist < 0.2:
        #turn left
        vel.angular.z += map_range(f_right_dist, 0.1, 0.2, 0.5, 0.2)
        print_values()
        return
    
    if f_left_dist < 0.2:
        #turn right
        vel.angular.z += -1 * map_range(f_left_dist, 0.1, 0.2, 0.5, 0.2)
        print_values()
        return

    print_values()
    

def print_values():
    global avg_speed, speed_sum, collisions, counter, is_collided
    counter += 1
    speed_sum += vel.linear.x
    avg_speed = speed_sum / counter
    print("ang", "{:.2f}".format(vel.angular.z), "lin","{:.2f}".format(vel.linear.x), "col", collisions, "avg_vel", "{:.2f}".format(avg_speed))
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
