import numpy as np
import matplotlib.pyplot as plt


def result_plots(plot_opts: dict,
                 refline: np.ndarray,
                 bound1_imp: np.ndarray,
                 bound2_imp: np.ndarray,
                 bound1_interp: np.ndarray,
                 bound2_interp: np.ndarray) -> None:
    """
    Created by:
    Alexander Heilmeier
    Modified by:
    Weiqi Lyu

    Documentation:
    This function plots several figures containing relevant track information after interpolation and smoothing.

    Inputs:
    plot_opts:      dict containing the information which figures to plot
    refline:        contains the reference line coordinates [x_m, y_m]
    bound1_imp:     first track boundary (as imported) (mostly right) [x_m, y_m]
    bound2_imp:     second track boundary (as imported) (mostly left) [x_m, y_m]
    bound1_interp:  first track boundary (interpolated) (mostly right) [x_m, y_m]
    bound2_interp:  second track boundary (interpolated) (mostly left) [x_m, y_m]
    """

    if plot_opts["centerline"]:

        point1_arrow = refline[0]
        point2_arrow = refline[3]
        vec_arrow = point2_arrow - point1_arrow

        # plot track including centerline
        plt.figure()
        plt.plot(refline[:, 0], refline[:, 1], "k--", linewidth=0.7)
        plt.plot(bound1_interp[:, 0], bound1_interp[:, 1], "k-", linewidth=0.7)
        plt.plot(bound2_interp[:, 0], bound2_interp[:, 1], "k-", linewidth=0.7)

        if plot_opts["imported_bounds"] and bound1_imp is not None and bound2_imp is not None:
            plt.plot(bound1_imp[:, 0], bound1_imp[:, 1], "y-", linewidth=0.7)
            plt.plot(bound2_imp[:, 0], bound2_imp[:, 1], "y-", linewidth=0.7)

        plt.grid()
        ax = plt.gca()
        # Set Arrow Size
        ax.arrow(point1_arrow[0], point1_arrow[1], vec_arrow[0], vec_arrow[1],
                 head_width=2.0, head_length=2.0, fc='g', ec='g')
        ax.set_aspect("equal", "datalim")
        plt.xlabel("east in m")
        plt.ylabel("north in m")
        plt.show()
        plt.savefig("track.png", dpi=300)


    if plot_opts["spline_normals"]:
        plt.figure()

        plt.plot(refline[:, 0], refline[:, 1], 'k-')
        for i in range(bound1_interp.shape[0]):
            temp = np.vstack((bound1_interp[i], bound2_interp[i]))
            plt.plot(temp[:, 0], temp[:, 1], "r-", linewidth=0.7)

        plt.grid()
        ax = plt.gca()
        ax.set_aspect("equal", "datalim")
        plt.xlabel("east in m")
        plt.ylabel("north in m")

        plt.show()
        plt.savefig("spline_normals.png", dpi=300)


# testing --------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    pass
