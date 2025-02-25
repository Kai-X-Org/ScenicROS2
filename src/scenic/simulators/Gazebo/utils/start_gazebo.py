from gazebo_msgs.srv import DeleteModel
import roslaunch
import rclpy
from std_srvs.srv import Empty

def PauseGazebo(node):
    """
    Pauses Gazebo
    """
    client = node.create_client(Empty, '/pause_physics')
    while not client.wait_for_service(timeout_sec=1.0):
        node.get_logger().info('service not available, waiting again...')

    resp = client.call_async()
    rclpy.spin_until_future_complete(node, resp)

    return


def UnpauseGazebo(node):
    """
    Unpauses Gazebo
    """
    client = node.create_client(Empty, '/unpause_physics')
    while not client.wait_for_service(timeout_sec=1.0):
        node.get_logger().info('service not available, waiting again...')

    resp = client.call_async()
    rclpy.spin_until_future_complete(node, resp)
    return


def ResetGazeboWorldAndSim(node):
    """
    Resets the Gazebo world and simulation
    Probably NOT the function you want to call in most cases
    This might cause the robot and ROS to go wild
    """
    # rospy.wait_for_service("/reset_world")
    # reset_world = rospy.ServiceProxy("/reset_world", Empty)
    # reset_world()

    # rospy.wait_for_service("/reset_simulation")
    # reset_simulation = rospy.ServiceProxy("/reset_simulation", Empty)
    # reset_simulation()
    client = node.create_client(Empty, '/reset_world')
    while not client.wait_for_service(timeout_sec=1.0):
        node.get_logger().info('service not available, waiting again...')

    resp = client.call_async()
    rclpy.spin_until_future_complete(node, resp)

    client = node.create_client(Empty, '/reset_simulation')
    while not client.wait_for_service(timeout_sec=1.0):
        node.get_logger().info('service not available, waiting again...')

    resp = client.call_async()
    rclpy.spin_until_future_complete(node, resp)
    return


def ResetGazeboWorld(node):
    """
    Resets the Gazebo world. Simulation time is NOT reset
    Probably the Reset function that you want
    """
    client = node.create_client(Empty, '/reset_world')
    while not client.wait_for_service(timeout_sec=1.0):
        node.get_logger().info('service not available, waiting again...')

    resp = client.call_async()
    rclpy.spin_until_future_complete(node, resp)
