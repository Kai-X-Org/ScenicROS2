
import math
import os
import sys

from gazebo_msgs.msg import ModelStates
from gazebo_msgs.srv import DeleteEntity
# from gazebo_msgs.srv import SetModelConfiguration
from gazebo_msgs.srv import SpawnEntity
# from geometry_msgs.msg import Pose
from lxml import etree as ElementTree
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSDurabilityPolicy
from rclpy.qos import QoSProfile
from std_msgs.msg import String
from std_srvs.srv import Empty

from geometry_msgs.msg import Pose, Quaternion

def DeleteObject(name, node, sim=None):
    """
    deletes the object from Gazebo and collision world
    Args:
    String name: the name of the object
    """
    # rospy.wait_for_service("/delete_entity")


    try:
        client = node.create_client(DeleteEntity, "/delete_entity")
        while not client.wait_for_service(timeout_sec=1.0):
            node.get_logger().info('service not available, waiting again...')
        
        req = DeleteEntity.Request()
        req.name = name
        resp = client.call_async(req)
        # resp = client.call_async(name)
        return (resp.success, resp.status_message)

    except Exception as e:
        node.get_logger().error("DeleteObject Fail Go")
        raise RuntimeError(f"Failed to delete object {name}")

def SpawnObject(
    name,
    object_xml,
    node,
    x=0,
    y=0,
    z=0,
    roll=0,
    pitch=0,
    yaw=0,
    file_type="sdf",
    ref_frame="map",  # TODO, FIX DOCUMENTATION AND RETURN VALS
    timeout=5.0,
):
    """
    Returns exit code, 1 for failure, 0 for success
    """

    # Load entity XML from file
    print('Loading entity XML from file %s' % object_xml)
    if not os.path.exists(object_xml):
        print('Error: specified file %s does not exist', object_xml)
        return 1
    if not os.path.isfile(object_xml):
        print('Error: specified file %s is not a file', object_xml)
        return 1
    # load file
    try:
        f = open(object_xml, 'r')
        entity_xml = f.read()
    except IOError as e:
        print('Error reading file')
        return 1
    if entity_xml == '':
        print('Error: file is empty')
        return 1

    # Parse xml to detect invalid xml before sending to gazebo
    try:
        xml_parsed = ElementTree.fromstring(entity_xml)
    except ElementTree.ParseError as e:
        print('Invalid XML: {}'.format(e))
        return 1

    # Encode xml object back into string for service call
    entity_xml = ElementTree.tostring(xml_parsed)

    # Form requested Pose from arguments
    initial_pose = Pose()
    initial_pose.position.x = float(x)
    initial_pose.position.y = float(y)
    initial_pose.position.z = float(z)

    q = quaternion_from_euler(roll, pitch, yaw)
    initial_pose.orientation.w = q[0]
    initial_pose.orientation.x = q[1]
    initial_pose.orientation.y = q[2]
    initial_pose.orientation.z = q[3]

    spawn_service_timeout = timeout
    success = _spawn_entity(name, node, entity_xml, initial_pose, spawn_service_timeout, reference_frame=ref_frame)
    if not success:
        print('Spawn service failed. Exiting.')
        return 1

    return 0

def _spawn_entity(name, node, entity_xml, initial_pose, timeout=5.0, reference_frame="", gazebo_namespace="", robot_namespace=""):
    if timeout < 0:
        node.get_logger().info('spawn_entity timeout must be greater than zero')
        return False

    node.get_logger().info()('Waiting for service %s/spawn_entity' % gazebo_namespace)

    client = node.create_client(SpawnEntity, '%s/spawn_entity' % gazebo_namespace)
    if client.wait_for_service(timeout_sec=timeout):
        req = SpawnEntity.Request()
        req.name = name 
        req.xml = str(entity_xml, 'utf-8')
        req.robot_namespace = robot_namespace
        req.initial_pose = initial_pose
        req.reference_frame = reference_frame
        node.get_logger().info('Calling service %s/spawn_entity' % gazebo_namespace)

        srv_call = client.call_async(req)
        while rclpy.ok():
            if srv_call.done():
                node.get_logger().info('Spawn status: %s' % srv_call.result().status_message)
                break
            rclpy.spin_once(node)

        return srv_call.result().success
    node.get_logger().info('Service %s/spawn_entity unavailable. Was Gazebo started with GazeboRosFactory?')

    return False


def quaternion_from_euler(roll, pitch, yaw):
    cy = math.cos(yaw * 0.5)
    sy = math.sin(yaw * 0.5)
    cp = math.cos(pitch * 0.5)
    sp = math.sin(pitch * 0.5)
    cr = math.cos(roll * 0.5)
    sr = math.sin(roll * 0.5)

    q = [0] * 4
    q[0] = cy * cp * cr + sy * sp * sr
    q[1] = cy * cp * sr - sy * sp * cr
    q[2] = sy * cp * sr + cy * sp * cr
    q[3] = sy * cp * cr - cy * sp * sr

    return q
