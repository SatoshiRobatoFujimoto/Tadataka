from autograd import numpy as np
from numpy.testing import assert_array_equal, assert_array_almost_equal

from bundle_adjustment.initializers import Initializer
from camera import CameraParameters
from rigid.transformation import transform_each
from rigid.rotation import rodrigues
from projection.projections import PerspectiveProjection


def test_initialize():
    def project(rotations, translations, points, camera_parameters):
        points = transform_each(rotations, translations, points)
        projection = PerspectiveProjection(camera_parameters)
        keypoints = projection.compute(points.reshape(-1, 3))
        keypoints = keypoints.reshape(points.shape[0], points.shape[1], 2)
        return keypoints


    camera_parameters = CameraParameters(
        focal_length=[0.9, 1.2],
        offset=[0.8, -0.2]
    )

    rotations_true = np.array([
        [[0, 1, 0],
         [1, 0, 0],
         [0, 0, -1]],
        [[0, -1, 0],
         [0, 0, -1],
         [1, 0, 0]]
    ])

    translations_true = np.array([
        [0, 0, 3],
        [0, 0, 2]
    ])

    points_true = np.array([
        [-1, -1, -1], [-1, -1, 0], [-1, -1, 1],
        [-1, 0, -1], [-1, 0, 0], [-1, 0, 1],
        [-1, 1, -1], [-1, 1, 0], [-1, 1, 1],
        [0, -1, -1], [0, -1, 0], [0, -1, 1],
        [0, 0, -1], [0, 0, 0], [0, 0, 1],
        [0, 1, -1], [0, 1, 0], [0, 1, 1],
        [1, -1, -1], [1, -1, 0], [1, -1, 1],
        [1, 0, -1], [1, 0, 0], [1, 0, 1],
        [1, 1, -1], [1, 1, 0], [1, 1, 1],
    ])

    keypoints_true = project(
        rotations_true, translations_true, points_true,
        camera_parameters
    )

    masks = np.ones(keypoints_true.shape[0:2], dtype=np.bool)
    initializer = Initializer(keypoints_true, camera_parameters.matrix)
    omegas_pred, translations_pred, points_pred = initializer.initialize()

    rotations_pred = rodrigues(omegas_pred)

    # camera poses and the reconstructed points have scale / rotation ambiguity
    # therefore we project the points and test if the projected points
    # match the original keypoints
    keypoints_pred = project(
        rotations_pred, translations_pred, points_pred,
        camera_parameters
    )

    assert_array_almost_equal(keypoints_true, keypoints_pred)
