# Perception-Mapping

This a repository that contains ready-to-run autonomous racing p


## Overview
- **centerline_generation**: Mapping process for centerline extraction and interpolation, modified based on the repository [Cl2-UWaterloo/Raceline-Optimization](https://github.com/CL2-UWaterloo/Raceline-Optimization).
- **maps**: Cleaned map and corresponding csv files for centerline and splines.


## Getting Started with Mapping
These are the high level steps followed to get the Rosbot driving in a new location, with [accompanying notes](https://stevengong.co/notes/F1TENTH-Field-Usage):
1. Run SLAM on the physical car to generate a map with [slam_toolbox](https://github.com/SteveMacenski/slam_toolbox) (reference the following [slides](https://docs.google.com/presentation/d/1DP2F9l-yHe9gQobk2CzYduk6KR5QtDCp7sLsxqR2fag/edit#slide=id.g115c48c178d_0_1) for running it on the physical car).
2. Clean up map with GIMP.
3. We recommand installing a virtualenv for `Mapping`.
```bash
git clone https://gitlab.lrz.de/felix-jahncke-students/ma_weiqilyu.git
virtualenv mapping
source mapping/bin/activate
cd MPCC-CBF/Mapping
pip3 install -r requirements.txt
```
4. Generate the centerline using `Mapping/centerline_f110.py`.
5. Store the maps and centerline under `maps`,  `rosbot/src/rosbot_mpcc/maps`, and `rosbot/src/mpcc_cbf/maps`.


## Getting Started with Centerline Generation
1. Clone the gym repository and follow the instructions from [f1tenth_gym](https://github.com/f1tenth/f1tenth_gym).
2. Copy the scripts in `Gym` to `gym`.
3. Change the map address in the main program of `gym/mpcc_gym` and `gym/mpcc_cbf_gym`.
4. Uncomment the statements about the gym environment in the planner or controller.
5. Run mpcc_gym.py to check the performance of planner_simple in the gym environment.
6. Run mpcc_cbf_gym.py to check the performance of controller in the gym environment.


## Getting Started in Real Car
If you want to try out the ROS nodes in real car, you can follow the steps below:

1. Change the waypoints path inside the [config.yaml](./rosbot/src/rosbot_mpcc/config/config.yaml) file (e.g. for planner with simple dynamics).
2. Change the map address inside the [mpcc.py](./rosbot/src/rosbot_mpcc/rosbot_mpcc/mpcc.py) file, and set SIM as False.
3. Change the map address inside the [mpcc_planner.py](./rosbot/src/rosbot_mpcc/rosbot_mpcc/mpcc_planner.py) file.
4. Change the map address inside the [track_interpolante.py](./rosbot/src/rosbot_mpcc/rosbot_mpcc/track_interpolante.py) file.
5. Open a terminal, source the ROS underlay, navigate to the workspace, build the workspace and source the overlay:
```bash
source /opt/ros/foxy/setup.bash
cd ROSBOT/rosbot
colcon build --symlink-install
source install/setup.bash
```    
6. Navigate into the f1tenth_ws workspace, source the underlay and overlay, and launch the Teleop package with:
```bash
cd f1tenth_ws
source /opt/ros/foxy/setup.bash
source install/setup.bash
ros2 launch f1tenth_stack bringup_launch.py
```
7. Store the map and centerline under `f1tenth_ws_waterloo/src/particle_filter/maps`, and update the map address in `f1tenth_ws_waterloo/src/particle_filter/localize.yaml`.
8. Open a new terminal, source the ROS underlay, navigate into the f1tenth_ws_waterloo workspace, and build the workspace:
```bash
source /opt/ros/foxy/setup.bash
cd f1tenth_ws_waterloo
colcon build --symlink-install
```   
9. Under the same terminal, set the PYTHONPATH, source the overlay, and launch the particle filter:
```bash
export PYTHONPATH=${PYTHONPATH}:/usr/lib/python3.8/site-packages/range_libc-0.1-py3.8-linux-aarch64.egg
source install/setup.bash
ros2 launch particle_filter localize_launch.py
``` 
10. Open a new terminal, navigate into the f1tenth workspace, source the under- and overlay, run e.g. the mpcc node via:
```bash
cd MPCC-CBF/f1tenth
source /opt/ros/foxy/setup.bash
source install/setup.bash
ros2 launch f1tenth_mpcc f1tenth_mpcc.py
```  
