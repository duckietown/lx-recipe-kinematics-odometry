#!/bin/bash

source /environment.sh

source /opt/ros/noetic/setup.bash
source /code/catkin_ws/devel/setup.bash --extend

exec roslaunch encoder_pose encoder_pose_node.launch veh:=$VEHICLE_NAME