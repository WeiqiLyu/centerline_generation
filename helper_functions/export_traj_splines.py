import numpy as np



def export_traj_splines(file_paths: dict,
                        spline_data,
                        reftrack,
                        normvec_normalized) -> None:
    """
    Created by:
    Weiqi Lyu

    Documentation:
    This function is used to export the centerline of the track into a file for further usage in the local trajectory
    planner on the car (including map information via normal vectors and bound widths).

    The stored trajectory has the following columns:
    [x_ref_m, y_ref_m, width_right_m, width_left_m, x_normvec_m, y_normvec_m, s_m, a0, a1, a2, a3, b0, b1, b2, b3]

    Inputs:
    file_paths:         paths for input and output files
    spline_data:        [spline_lengths, coeffs_x, coeffs_y]
    reftrack:           track definition [x_m, y_m, w_tr_right_m, w_tr_left_m]
    normvec_normalized: normalized normal vectors on the reference line [x_m, y_m]
    """

    # convert trajectory to desired format
    spline_lengths = spline_data[:,0]                    #lengths of the splines on the raceline in m
    coefficient_x = spline_data[:,1:5]
    coefficient_y = spline_data[:,5:]

    traj = np.column_stack((reftrack,normvec_normalized))
    spline = np.column_stack((spline_lengths,coefficient_x,coefficient_y))
    
    # export trajectory data for local planner
    header_1 = "x_ref_m; y_ref_m; width_right_m; width_left_m; x_normvec_m; y_normvec_m" 
    fmt = "%.7f; %.7f; %.7f; %.7f; %.7f; %.7f"
    with open(file_paths["traj_export"], 'ab') as fh:
        np.savetxt(fh, traj, fmt=fmt, header=header_1, comments='')

    # export spline data for local planner
    header_2 = "s_m; a0; a1; a2; a3; b0; b1; b2; b3"
    fmt = "%.7f; %.7f; %.7f; %.7f; %.7f; %.7f; %.7f; %.7f; %.7f"
    with open(file_paths["spline_export"], 'ab') as fh:
        np.savetxt(fh, spline, fmt=fmt, header=header_2, comments='')

# testing --------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    pass
