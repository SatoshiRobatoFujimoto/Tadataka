from autograd import numpy as np
from matplotlib.animation import FuncAnimation
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

from tadataka.rigid_transform import inv_transform_all
from tadataka.so3 import rodrigues
from tadataka.rigid.coordinates import camera_to_world
from tadataka.plot.visualizers import object_color
from tadataka.plot.cameras import cameras_poly3d


class VisualOdometryAnimation(object):
    def __init__(self, fig, ax, frames, interval=100, camera_scale=1.0):
        self.ax = ax
        self.animation = FuncAnimation(fig, self.animate, frames=frames,
                                       interval=interval)
        self.camera_scale = camera_scale

    def animate(self, args):
        camera_omegas, camera_locations, points = args

        cameras = cameras_poly3d(rodrigues(camera_omegas), camera_locations,
                                 self.camera_scale)
        points_ = self.ax.scatter(points[:, 0], points[:, 1], points[:, 2],
                                  c=object_color(points))
        return cameras, points_

    def plot(self):
        plt.show()