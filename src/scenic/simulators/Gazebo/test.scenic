from scenic.simulators.Gazebo.model import *

simulator GazeboSimulator()

shelf = new BookShelf on (Range(0, 2), 0, 0), with yaw Range(0, 360) deg
shelf = new BookShelf on (0, Range(0, 2), 0), with name "shelf2"
