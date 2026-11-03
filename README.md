# LX Recipe: Kinematics and Odometry (ROS 2)

Recipe of the [lx-kinematics-odometry](https://github.com/duckietown/lx-kinematics-odometry) Learning Experience
(solution: [lx-kinematics-odometry-solution](https://github.com/duckietown/lx-kinematics-odometry-solution)).
The LX runs on the ROS 2 (Jazzy, `rmw_zenoh_cpp`) robot stack of the `ente` distribution; there is no remote desktop
any more, every tool the students used to open on the desktop is a notebook panel.

## What the recipe provides

- `Dockerfile` / `launchers/default.sh`: the workbench image (`dts code workbench`) is based on `dt-ros2-commons`,
  builds `packages/` with colcon and runs `ros2 launch encoder_pose encoder_pose_node.launch.py veh:=ROBOT`
  (the `encoder_pose` package is the student's code, it comes from the LX repository).
- `Dockerfile.vscode` / `dependencies-apt.vscode.txt` / `assets/vscode/`: the code editor image (`dts code editor`)
  with ROS 2 and the Duckietown messages installed, so that the notebooks and the editor terminal talk to the
  robot (`ros2 topic echo ...`, notebook panels).
- `packages/lx_ros2_tools/`: helpers shared by all the ROS 2 LXs (`RosSession`, `ParamPanel`, `ActionButtons`,
  `ImageView`, `TopicPlot`, `TrajectoryPlot`, `LiveParams`, `get_wheel_params`).
- `packages/lx_kinematics_tools/`: `Joystick`, the virtual joystick used by the notebooks of this LX (publishes
  `Twist2DStamped` on `car_cmd_switch_node/cmd`; `Joystick(ros, topic="car_cmd")` for older robot images whose
  `kinematics_node` still listens on `/ROBOT/car_cmd`, see `ros2 node info /ROBOT/kinematics_node`).
- `packages/simulators/`: kinematics/dynamics simulators used by the notebooks.
- `assets/duckiematrix/`: the Duckiematrix map (`settings.yaml` selects it).

## Student node (LX repository)

`packages/encoder_pose` (ament_python): the `encoder_pose_node` subscribes to
`left_wheel_encoder_driver_node/tick` and `right_wheel_encoder_driver_node/tick` (`duckietown_msgs/WheelEncoderStamped`),
reads the wheel radius / baseline from the robot calibration file (`/data/config/calibrations/robot/ROBOT.yaml`,
via `lx_ros2_tools.robot.get_wheel_params`) and publishes the estimated pose as `nav_msgs/Odometry` on
`encoder_pose_node/odom`. Parameters: `publish_rate`, `verbose`. Service: `encoder_pose_node/reset` (`std_srvs/Trigger`).
The functions the students implement live in `packages/odometry/odometry.py` (imported by both the node and the notebooks).

## Testing the recipe locally

```
dts code build -R ROBOT          # workbench image
dts code workbench -R ROBOT      # runs the node against the robot (-m for the Duckiematrix)
dts code editor                  # notebooks + ros2 CLI
```
