import rospy
import numpy as np
from gazebo_plugins.gazebo_ros_utils import GazeboRosModelPlugin

PROP_DIAMETER = 0.254  # m
PROP_PITCH = 0.1143  # m
AIR_DENSITY = 1.225  # kg/m^3
LIFT_COEFFICIENT = 0.042
DRAG_COEFFICIENT = 0.031


class AerodynamicsModelPlugin(GazeboRosModelPlugin):
    def __init__(self):
        super(AerodynamicsModelPlugin, self).__init__()

    def Load(self, model, sdf):
        super(AerodynamicsModelPlugin, self).Load(model, sdf)

        # Get motor joint names from the SDF file
        self.motor_joints = []
        for i in range(sdf.attrib['motorJointCount']):
            self.motor_joints.append(sdf.attrib[f'motorJoint{i+1}'])

        self.update_rate = rospy.Rate(50)  # Hz
        self.start_physics_update_thread(self.update_aerodynamics)

    def update_aerodynamics(self):
        # Calculate lift and drag forces for each propeller
        forces = []
        for joint_name in self.motor_joints:
            joint = self.model.get_joint(joint_name)
            speed_rad = joint.get_velocity(0)

            # Convert rad/s to RPM
            speed_rpm = speed_rad * 60 / (2 * np.pi)

            # Calculate lift and drag forces
            lift_force = 0.5 * LIFT_COEFFICIENT * AIR_DENSITY * (PROP_DIAMETER**2) * (speed_rpm * PROP_PITCH / 60)**2
            drag_force = 0.5 * DRAG_COEFFICIENT * AIR_DENSITY * (PROP_DIAMETER**2) * (speed_rpm * PROP_PITCH / 60)**2

            forces.append((lift_force, drag_force))

        # Calculate total forces and moments
        total_force, total_moment = self.calculate_total_forces_and_moments(forces)

        # Apply the calculated forces and moments to the drone's body
        self.model.set_link_world_force("base_link", total_force)
        self.model.set_link_world_torque("base_link", total_moment)

        self.update_rate.sleep()

    def calculate_total_forces_and_moments(self, forces):
        total_force = np.zeros(3)
        total_moment = np.zeros(3)

        for i, (lift_force, drag_force) in enumerate(forces):
            motor_pos, motor_rot = self.get_motor_position_and_orientation(i)
            force_vector = lift_force * motor_rot - drag_force * motor_rot
            total_force += force_vector
            total_moment += np.cross(motor_pos, force_vector)

        return total_force, total_moment

    def get_motor_position_and_orientation(self, motor_index):
        motor_positions = [
            np.array([1, 1, 0]),
            np.array([1, -1, 0]),
            np.array([-1, -1, 0]),
            np.array([-1, 1, 0])
        ]

        motor_orientations = [
            np.array([0, 0, 1]),
            np.array([0, 0, 1]),
            np.array([0, 0, 1]),
            np.array([0, 0, 1])
        ]

        return motor_positions[motor_index], motor_orientations[motor_index]

