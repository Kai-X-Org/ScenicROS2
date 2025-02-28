from scenic.simulators.Gazebo.model import *

simulator GazeboSimulator()

ego = new BookShelf on (0, 0, 0), with yaw Range(0,360) deg, with color (0,0,0)
# shelf = new BookShelf on (0, 3, 0), with name "shelf2", with color (1, 0, 0)
shelf = new BookShelf ahead of ego by 3, with name "shelf2", with yaw 90 deg
