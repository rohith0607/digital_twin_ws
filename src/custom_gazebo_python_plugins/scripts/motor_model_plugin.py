import rospy
import sys
sys.path.insert(0, '/opt/ros/noetic/share/gazebo_plugins')
import numpy as np
from gazebo_plugins.gazebo_ros_utils import GazeboRosModelPlugin
from std_msgs.msg import Float64

ESC_MAX_CURRENT = 30.0  # A
ESC_BEC_VOLTAGE = 5.0  # V
BATTERY_CAPACITY = 2200  # mAh
BATTERY_VOLTAGE = 11.1  # V
BATTERY_DISCHARGE_RATE = 25  # C-rating

MOTOR_MAX_TORQUE = 0.289  # Nm
MOTOR_MAX_SPEED = 11100  # RPM
MOTOR_EFFICIENCY = 0.8
MOTOR_KV = 1000  # RPM/Volt
MOTOR_KT = 0.024  # N.m/Amp


class MotorModelPlugin(GazeboRosModelPlugin):
    def __init__(self):
        super(MotorModelPlugin, self).__init__()

    def Load(self, model, sdf):
        super(MotorModelPlugin, self).Load(model, sdf)

        # Get motor joint names from the SDF file
        self.motor_joints = []
        for i in range(sdf.attrib['motorJointCount']):
            self.motor_joints.append(sdf.attrib[f'motorJoint{i+1}'])

        # Initialize motor joint subscribers
        self.subs = []
        for joint in self.motor_joints:
            sub = rospy.Subscriber(f'{joint}_cmd', Float64, self.update_joint, callback_args=joint)
            self.subs.append(sub)

    def update_joint(self, msg, joint):
        # Get the desired motor speed in RPM from the message
        desired_speed = msg.data

        # Convert RPM to rad/s
        desired_speed_rad = desired_speed * (2 * np.pi) / 60

        # Calculate motor current based on torque
        current = MOTOR_MAX_TORQUE / MOTOR_KT

        # Calculate voltage based on motor speed and current
        voltage = desired_speed_rad / MOTOR_KV + current / MOTOR_EFFICIENCY

        # Cap the voltage to the battery voltage
        voltage = min(voltage, BATTERY_VOLTAGE)

        # Calculate the new motor speed
        speed_rad = (voltage - current / MOTOR_EFFICIENCY) * MOTOR_KV

        # Set the new motor speed
        self.set_joint_velocity(joint, speed_rad)

    def set_joint_velocity(self, joint_name, velocity):
        joint = self.model.get_joint(joint_name)
        joint.set_velocity(0, velocity)


if __name__ == '__main__':
    rospy.init_node('motor_model_plugin', anonymous=True)
    motor_model = MotorModelPlugin()
    rospy.spin()
