from gazebo_msgs.msg import ModelState
from gazebo_msgs.srv import (
    GetModelProperties,
    GetEntityState,
    GetWorldProperties,
    SetEntityState,
)
from geometry_msgs.msg import (
    Pose,
    PoseStamped,
    PoseWithCovarianceStamped,
    TransformStamped,
    Vector3,
    Twist
)
# from tf.transformations import euler_from_quaternion, quaternion_from_euler

# from geometry_msgs.msg import Quaternion
# import rospy
import rclpy

# import tf_conversions
import numpy as np
import tf2_geometry_msgs
import tf2_ros


def GetObjectPose(obj, node, frame="map"):  # works
    """
    String obj: the name of the object
    String frame: the reference frame for the pose
    Returns: dictionary containing pose information
    """
    state = GetObjectGazeboState(obj, node, frame=frame)
    if state:
        pos = state.pose.position
        ori = state.pose.orientation
        ori = euler_from_quaternion([ori.x, ori.y, ori.z, ori.w])
        # return (pos.x, pos.y, pos.z, ori[-1])
        return dict(x=pos.x, y=pos.y, z=pos.z, roll=ori[0], pitch=ori[1], yaw=ori[-1])

    return None


def GetObjectState(obj, node, frame="map"):
    """
    Probably what you want to call to get an object's current states
    String obj: the name of the object
    String frame: the reference frame for the pose
    Returns: dictionary containing state information
    """
    try:
        state = GetObjectGazeboState(obj, node, frame)
        if state:
            pos = state.pose.position
            ori = state.pose.orientation
            ori = euler_from_quaternion([ori.x, ori.y, ori.z, ori.w])
            linear = state.twist.linear
            angular = state.twist.angular
            state = dict(
                x=pos.x,
                y=pos.y,
                z=pos.z,
                roll=ori[0],
                pitch=ori[1],
                yaw=ori[-1],
                speed=np.linalg.norm(np.array([linear.x, linear.y, linear.z])),
                velocity=linear,
                angularSpeed=np.linalg.norm(np.array([angular.x, angular.y, angular.z])),
                angularVelocity=angular,
            )
        return state
    except Exception as e:
        rospy.logerr("GetObjectState Fail go")
        raise e


def GetObjectGazeboState(obj, node, frame="map"):
    """
    String obj: the name of the object
    String frame: the reference frame for the pose
    Returns: gazebo_msgs.msg.ModelState
    """
    try:

        client = node.create_client(GetEntityState, '/gazebo/get_entity_states')
        while not client.wait_for_service(timeout_sec=1.0):
            node.get_logger().info('get_entity_states service not available, waiting again...')
        
        # TODO maybe should get an instance of GetEntityState.request and fill in the fields?
        req = GetEntityState.Request()
        req.name = obj
        req.reference_frame = frame
        resp = client.call_async(req)
        rclpy.spin_until_future_complete(node, resp) 
        return resp

    except Exception as e:
        node.get_logger().error("GetObjectGazeboState Fail go")
        raise RuntimeError(
            f"Failed to get obj.namer state; Gazebo\
                           get_model_state service failed with exception {e}"
        )



def SetModelPose(
    tgt_model, node, x=0.0, y=0.0, z=0.0, roll=0, pitch=0, yaw=0.0, frame="map"
):  # Good
    """
    Set the Model's Pose
    Args:
    String tgt_model: name of model
    float x: x position
    float y: y position
    float z: z position
    float Yaw: angle
    Returns: Typle(bool success, String status_message)
    """
    ref_frame_id = frame

    # rospy.wait_for_service("/gazebo/get_entity_state")
    # get_model_state = rospy.ServiceProxy("/gazebo/get_entity_state", GetEntityState)
    # model_state = get_model_state(tgt_model, "")

    client = node.create_client(GetEntityState, '/gazebo/get_entity_states')
    while not client.wait_for_service(timeout_sec=1.0):
        node.get_logger().info('get_entity_states service not available, waiting again...')
    
    # TODO maybe should get an instance of GetEntityState.request and fill in the fields?
    req = GetEntityState.Request()
    req.name = tgt_model
    req.reference_frame = frame
    resp = client.call_async(req)
    rclpy.spin_until_future_complete(node, resp)

    quat = quaternion_from_euler(roll, pitch, yaw)

    new_pose = Pose()
    new_pose.position.x = x
    new_pose.position.y = y
    new_pose.position.z = z
    new_pose.orientation.x = quat[0]
    new_pose.orientation.y = quat[1]
    new_pose.orientation.z = quat[2]
    new_pose.orientation.w = quat[3]

    new_model_state = ModelState()
    new_model_state.model_name = tgt_model
    new_model_state.pose = new_pose
    new_model_state.twist = geometry_msgs.Twist()
    new_model_state.reference_frame = frame

    # rospy.wait_for_service("/gazebo/set_entity_state")
    # set_state = rospy.ServiceProxy("/gazebo/set_entity_state", SetEntityState)
    # resp = set_state(new_model_state)

    client = node.create_client(GetEntityState, '/gazebo/get_entity_states')
    while not client.wait_for_service(timeout_sec=1.0):
        node.get_logger().info('get_entity_states service not available, waiting again...')
    
    # TODO maybe should get an instance of GetEntityState.request and fill in the fields?
    req = GetEntityState.Request()
    req.name = tgt_model
    req.reference_frame = frame
    resp = client.call_async(req)
    rclpy.spin_until_future_complete(node, resp)

    return (resp.success, resp.status_message)


def ApplyROSTransform(transform, x=0, y=0, z=0, quat=(0, 0, 0, 1)):
    """
    transform: rospy.TransformStamped
    x, y, z: position
    quat: a quaternion (any indexable object is fine)
    returns
        Pose
    """
    pose_stamped = PoseStamped()
    pose = Pose()
    pose.position.x = x
    pose.position.y = y
    pose.position.z = z
    pose.orientation.x = quat[0]
    pose.orientation.y = quat[1]
    pose.orientation.z = quat[2]
    pose.orientation.w = quat[3]

    new_pose = tf2_geometry_msgs.do_transform_pose(pose, transform)
    return new_pose.pose


# def ListenToTransform(source, target):
    # """
    # Get the ROS transform from the source frame to the target frame
    # Args:
        # source: String
            # The source frame of reference
        # target: Target
            # The target frame of reference
    # Returns:
        # trans: rospy.TransformStamped
    # """
    # tfBuffer = tf2_ros.Buffer()
    # listener = tf2_ros.TransformListener(tfBuffer)
    # while not rospy.is_shutdown():
        # try:
            # trans = tfBuffer.lookup_transform(source, target, rospy.Time())
            # break
        # except:
            # continue
    # return trans

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
