import numpy as np
import time
import json
import configparser
import argparse
import os
from helper_functions import import_track, prep_track, calc_spline_lengths, interp_splines, calc_head_curv_an
from helper_functions import check_traj, export_traj_splines, calc_splines

"""
This script has to be executed for smmothing the centerline and get the cubic spline interpretation.
"""


# Create the parser and add arguments with defaults and explicit names
parser = argparse.ArgumentParser(description='Generate interpolated and smoothed track centerlines.')
parser.add_argument('--map_name', type=str, default='big_track_new', help='Name of the map (default: Hockenheim_map)')
parser.add_argument('--map_path', type=str, default='', help='Path to the map centerline (should be a .csv), defaults to tracks/<map_name>.csv')
parser.add_argument('--export_path', type=str, default='', help='Path to copy from the filepath in the /outputs')

args = parser.parse_args()

# Use the arguments
MAP_NAME = args.map_name
MAP_PATH = args.map_path
EXPORT_PATH = args.export_path

# ----------------------------------------------------------------------------------------------------------------------
# USER INPUT -----------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------

# choose vehicle parameter file 
# "f110.ini" for F1TENTH
# "rosbot.ini" for Rosbot
file_paths = {"veh_params_file": "f110.ini"}                    

# select track file (including centerline coordinates + track widths) 
file_paths["track_name"] = MAP_NAME

# initialization of paths 
file_paths["module"] = os.path.dirname(os.path.abspath(__file__))
file_paths["module"] = file_paths["module"].replace('\\', '/')
if MAP_PATH == '':
    MAP_PATH = os.path.join(file_paths["module"], "grob_tracks", file_paths["track_name"] + ".csv")
file_paths["track_file"] = MAP_PATH

# create outputs folder(s) 
os.makedirs(file_paths["module"] + f"/outputs", exist_ok=True)
file_paths["traj_export"] = os.path.join(file_paths["module"], f"outputs", f"{MAP_NAME}_centerline.csv")
file_paths["spline_export"] = os.path.join(file_paths["module"], f"outputs", f"{MAP_NAME}_splines.csv")

# ----------------------------------------------------------------------------------------------------------------------
# IMPORT VEHICLE DEPENDENT PARAMETERS ----------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------

# load vehicle parameter file into a "pars" dict 
parser = configparser.ConfigParser()
pars = {}

if not parser.read(os.path.join(file_paths["module"], file_paths["veh_params_file"])):
    raise ValueError('Specified config file does not exist or is empty!')

pars["stepsize_opts"] = json.loads(parser.get('GENERAL_OPTIONS', 'stepsize_opts'))
pars["reg_smooth_opts"] = json.loads(parser.get('GENERAL_OPTIONS', 'reg_smooth_opts'))
pars["veh_params"] = json.loads(parser.get('GENERAL_OPTIONS', 'veh_params'))

# set import options 
imp_opts = {"flip_imp_track": False,                # flip imported track to reverse direction
            "set_new_start": True,                  # set new starting point (changes order, not coordinates)
            "new_start": np.array([0.0, 0.0]),      # [x_m, y_m]
            "min_track_width": None,                # [m] minimum enforced track width (set None to deactivate)
            "num_laps": 1}                          # number of laps to be driven (significant with powertrain-option),
                                                    # only relevant in mintime-optimization
# debug and plot options 
debug = True                                    # print console messages
plot_opts = {"mincurv_curv_lin": False,         # plot curv. linearization (original and solution based) (mincurv only)
             "raceline": True,                  # plot optimized path
             "imported_bounds": True,           # plot imported bounds (analyze difference to interpolated bounds)
             "raceline_curv": False,            # plot curvature profile of optimized path
             "racetraj_vel": True,              # plot velocity profile
             "racetraj_vel_3d": True,           # plot 3D velocity profile above raceline
             "racetraj_vel_3d_stepsize": 0.5,   # [m] vertical lines stepsize in 3D velocity profile plot
             "spline_normals": False,           # plot spline normals to check for crossings
             "mintime_plots": False}            # plot states, controls, friction coeffs etc. (mintime only)

# ----------------------------------------------------------------------------------------------------------------------
# IMPORT TRACK AND VEHICLE DYNAMICS INFORMATION ------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------

# save start time
t_start = time.perf_counter()

# import track from new starting point
reftrack_imp = import_track.import_track(imp_opts=imp_opts,
                                         file_path=file_paths["track_file"],
                                         width_veh=pars["veh_params"]["width"])

# ----------------------------------------------------------------------------------------------------------------------
# PREPARE REFTRACK -----------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------

reftrack_interp, normvec_normalized_interp, a_interp, coeffs_x_interp, coeffs_y_interp = \
    prep_track.prep_track(reftrack_imp=reftrack_imp,
                          reg_smooth_opts=pars["reg_smooth_opts"],
                          stepsize_opts=pars["stepsize_opts"],
                          debug=debug,
                          min_width=imp_opts["min_track_width"])

# ----------------------------------------------------------------------------------------------------------------------
# INTERPOLATE SPLINES TO SMALL DISTANCES BETWEEN CENTERLINE POINTS -------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------

# calculate spline lengths     len(spline_lengths_centerline) = coeffs_x.shape[0]
spline_lengths_centerline = calc_spline_lengths.calc_spline_lengths(coeffs_x=coeffs_x_interp, coeffs_y=coeffs_y_interp)

# interpolate splines for evenly spaced centerline points
centerline_interp, spline_inds_centerline_interp, t_values_centerline_interp, s_centerline_interp = \
    interp_splines.interp_splines(spline_lengths=spline_lengths_centerline,
                                    coeffs_x=coeffs_x_interp,
                                    coeffs_y=coeffs_y_interp,
                                    incl_last_point=False,
                                    stepsize_approx=pars["stepsize_opts"]["stepsize_interp_after_opt"])

# calculate element lengths
#s_tot_centerline = float(np.sum(spline_lengths_centerline))
#el_lengths_centerline_interp = np.diff(s_centerline_interp)
#el_lengths_centerline_interp_cl = np.append(el_lengths_centerline_interp, s_tot_centerline - s_centerline_interp[-1])

# ----------------------------------------------------------------------------------------------------------------------
# CALCULATE HEADING AND CURVATURE --------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------

# calculate heading and curvature (analytically)
psi_vel, kappa = calc_head_curv_an.calc_head_curv_an(coeffs_x=coeffs_x_interp,
                                                             coeffs_y=coeffs_y_interp,
                                                             ind_spls=spline_inds_centerline_interp,
                                                             t_spls=t_values_centerline_interp)

# ----------------------------------------------------------------------------------------------------------------------
# DATA POSTPROCESSING --------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------

# arrange data into one trajectory
trajectory = np.column_stack((s_centerline_interp,centerline_interp,psi_vel,kappa))            # [n_new * (1 + 2 + 1 + 1)]

spline_data = np.column_stack((spline_lengths_centerline, coeffs_x_interp, coeffs_y_interp))   # [n * (1 + 4 + 4)]

# create a closed race trajectory array
#traj_centerline_cl = np.vstack((trajectory, trajectory[0, :]))
#traj_centerline_cl[-1, 0] = np.sum(spline_data[:, 0])  # set correct length

# print end time
print("INFO: Runtime from import to final trajectory was %.2fs" % (time.perf_counter() - t_start))

# ----------------------------------------------------------------------------------------------------------------------
# CHECK TRAJECTORY -----------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------

bound1, bound2 = check_traj.check_traj(reftrack=reftrack_interp,
                                       reftrack_normvec_normalized=normvec_normalized_interp,
                                       length_veh=pars["veh_params"]["length"],
                                       width_veh=pars["veh_params"]["width"],
                                       debug=debug,
                                       trajectory=trajectory,
                                       curvlim=pars["veh_params"]["curvlim"])

# ----------------------------------------------------------------------------------------------------------------------
# EXPORT ---------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# export trajectory and spline data  to CSV
export_traj_splines.export_traj_splines(file_paths=file_paths,
                                        spline_data=spline_data,
                                        reftrack=reftrack_interp,
                                        normvec_normalized=normvec_normalized_interp)

print("INFO: Finished export of trajectory:", time.strftime("%H:%M:%S"))


# ----------------------------------------------------------------------------------------------------------------------
# PLOT RESULTS ---------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------

# get bound of imported map (for reference in final plot)
bound1_imp = None
bound2_imp = None

if plot_opts["imported_bounds"]:
    # try to extract four times as many points as in the interpolated version (in order to hold more details)
    n_skip = max(int(reftrack_imp.shape[0] / (bound1.shape[0] * 4)), 1)

    _, _, _, normvec_imp = calc_splines.calc_splines(path=np.vstack((reftrack_imp[::n_skip, 0:2],
                                                                         reftrack_imp[0, 0:2])))

    bound1_imp = reftrack_imp[::n_skip, :2] + normvec_imp * np.expand_dims(reftrack_imp[::n_skip, 2], 1)
    bound2_imp = reftrack_imp[::n_skip, :2] - normvec_imp * np.expand_dims(reftrack_imp[::n_skip, 3], 1)
