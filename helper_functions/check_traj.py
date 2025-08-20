import numpy as np
from helper_functions import interp_track, calc_min_bound_dists


def check_traj(reftrack: np.ndarray,
               reftrack_normvec_normalized: np.ndarray,
               trajectory: np.ndarray,
               length_veh: float,
               width_veh: float,
               debug: bool,
               curvlim: float) -> tuple:
    """
    Created by:
    Alexander Heilmeier

    Documentation:
    This function checks the generated trajectory in regards of minimum distance to the boundaries and maximum
    curvature.

    Inputs:
    reftrack:           track [x_m, y_m, w_tr_right_m, w_tr_left_m]
    reftrack_normvec_normalized: normalized normal vectors on the reference line [x_m, y_m]
    trajectory:         trajectory to be checked [s_m, x_m, y_m, psi_rad, kappa_radpm]
    length_veh:         vehicle length in m
    width_veh:          vehicle width in m
    debug:              boolean showing if debug messages should be printed
    curvlim:            [rad/m] maximum drivable curvature

    Outputs:
    bound_r:            right track boundary [x_m, y_m]
    bound_l:            left track boundary [x_m, y_m]
    """

    # ------------------------------------------------------------------------------------------------------------------
    # CHECK VEHICLE EDGES FOR MINIMUM DISTANCE TO TRACK BOUNDARIES -----------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------

    # calculate boundaries and interpolate them to small stepsizes (currently linear interpolation)
    bound_r = reftrack[:, :2] + reftrack_normvec_normalized * np.expand_dims(reftrack[:, 2], 1)
    bound_l = reftrack[:, :2] - reftrack_normvec_normalized * np.expand_dims(reftrack[:, 3], 1)

    # check boundaries for vehicle edges
    bound_r_tmp = np.column_stack((bound_r, np.zeros((bound_r.shape[0], 2))))
    bound_l_tmp = np.column_stack((bound_l, np.zeros((bound_l.shape[0], 2))))

    bound_r_interp = interp_track.interp_track(
        track=bound_r_tmp, 
        stepsize=1.0, 
        original_figname = "original_right_boundary.png", 
        linear_interpolated_figname = "linear_interpolated_right_boundary.png")[0]
    
    bound_l_interp = interp_track.interp_track(
        track=bound_l_tmp, 
        stepsize=1.0,
        original_figname = "original_left_boundary.png", 
        linear_interpolated_figname = "linear_interpolated_left_boundary.png")[0]

    # calculate minimum distances of every trajectory point to the boundaries
    min_dists = calc_min_bound_dists.calc_min_bound_dists(trajectory=trajectory,
                                                          bound1=bound_r_interp,
                                                          bound2=bound_l_interp,
                                                          length_veh=length_veh,
                                                          width_veh=width_veh)

    # calculate overall minimum distance
    min_dist = np.amin(min_dists)

    # warn if distance falls below a safety margin of 1.0 m
    if min_dist < 1.0:
        print("WARNING: Minimum distance to boundaries is estimated to %.2fm. Keep in mind that the distance can also"
              " lie on the outside of the track!" % min_dist)
    elif debug:
        print("INFO: Minimum distance to boundaries is estimated to %.2fm. Keep in mind that the distance can also lie"
              " on the outside of the track!" % min_dist)

    # ------------------------------------------------------------------------------------------------------------------
    # CHECK FINAL TRAJECTORY FOR MAXIMUM CURVATURE ---------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------

    # check maximum (absolute) curvature
    if np.amax(np.abs(trajectory[:, 4])) > curvlim:
        print("WARNING: Curvature limit is exceeded: %.3frad/m" % np.amax(np.abs(trajectory[:, 4])))

    return bound_r, bound_l


# testing --------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    pass
