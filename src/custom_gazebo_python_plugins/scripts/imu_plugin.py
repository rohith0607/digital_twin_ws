import rospy
import numpy as np
from gazebo_plugins.gazebo_ros_utils import GazeboRosModelPlugin
from sensor_msgs.msg import Imu


class IMUPlugin(GazeboRosModelPlugin):
    def __init__(self):
        super(IMUPlugin, self).__init__()

    def Load(self, model, sdf):
        super(IMUPlugin, self).Load(model, sdf)

        # Initialize ROS publisher
        self.imu_pub = rospy.Publisher('imu', Imu, queue_size=10)

        # Define sensor noise characteristics
        self.accel_noise_stddev = 0.0025  # Replace with appropriate value
        self.gyro_noise_stddev = 0.0025   # Replace with appropriate value
        self.mag_noise_stddev = 0.0025    # Replace with appropriate value

        self.update_rate = rospy.Rate(100)  # Hz
        self.start_physics_update_thread(self.update_imu)

    def update_imu(self):
        # Read the true acceleration, angular velocity, and magnetic field values
        true_accel = self.model.get_link_world_linear_accel("base_link")
        true_gyro = self.model.get_link_world_angular_vel("base_link")
        true_mag = self.model.get_world_magnetic_field("base_link")

        # Add noise to the sensor readings
        noisy_accel = true_accel + np.random.normal(0, self.accel_noise_stddev, 3)
        noisy_gyro = true_gyro + np.random.normal(0, self.gyro_noise_stddev, 3)
        noisy_mag = true_mag + np.random.normal(0, self.mag_noise_stddev, 3)

        # Create an Imu message
        imu_msg = Imu()
        imu_msg.header.stamp = rospy.Time.now()
        imu_msg.header.frame_id = "base_link"

        # Fill in the message with the noisy sensor readings
        imu_msg.linear_acceleration.x = noisy_accel[0]
        imu_msg.linear_acceleration.y = noisy_accel[1]
        imu_msg.linear_acceleration.z = noisy_accel[2]

        imu_msg.angular_velocity.x = noisy_gyro[0]
        imu_msg.angular_velocity.y = noisy_gyro[1]
        imu_msg.angular_velocity.z = noisy_gyro[2]

        # Publish the message
        self.imu_pub.publish(imu_msg)

        self.update_rate.sleep()


if __name__ == '__main__':
    rospy.init_node('imu_plugin', anonymous=True)
    imu_plugin = IMUPlugin()
    rospy.spin()
