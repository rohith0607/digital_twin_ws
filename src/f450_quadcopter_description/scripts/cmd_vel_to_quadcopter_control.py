#!/usr/bin/env python

import rospy
from geometry_msgs.msg import Twist
from std_msgs.msg import Float64

# Constants for motor names
MOTOR1 = 'front_right_propeller_joint_position_controller/command'
MOTOR2 = 'front_left_propeller_joint_position_controller/command'
MOTOR3 = 'back_right_propeller_joint_position_controller/command'
MOTOR4 = 'back_left_propeller_joint_position_controller/command'

# Function to map linear and angular velocities to motor speeds
def map_twist_to_motor_speeds(twist):
    thrust = twist.linear.z
    pitch = twist.linear.x
    roll = twist.linear.y
    yaw_rate = twist.angular.z

    motor_speeds = [
        thrust + pitch - roll - yaw_rate,
        thrust - pitch - roll + yaw_rate,
        thrust - pitch + roll - yaw_rate,
        thrust + pitch + roll + yaw_rate,
    ]

    return motor_speeds

def cmd_vel_callback(msg):
    motor_speeds = map_twist_to_motor_speeds(msg)

    for pub, speed in zip(motor_pubs, motor_speeds):
        pub.publish(speed)

if __name__ == '__main__':
    rospy.init_node('cmd_vel_to_quadcopter_control')

    # Create publishers for the motor control commands
    motor_pubs = [
        rospy.Publisher(MOTOR1, Float64, queue_size=1),
        rospy.Publisher(MOTOR2, Float64, queue_size=1),
        rospy.Publisher(MOTOR3, Float64, queue_size=1),
        rospy.Publisher(MOTOR4, Float64, queue_size=1),
    ]

    # Subscribe to the /cmd_vel topic
    rospy.Subscriber('/cmd_vel', Twist, cmd_vel_callback)

    rospy.spin()
