from numpy.testing import assert_array_almost_equal, assert_array_equal
from autograd import numpy as np

from vitamine.local_ba import LocalBundleAdjustment, Projection, IndexConverter
from tests.utils import unit_uniform


def to_poses(omegas, translations):
    return np.hstack((omegas, translations))


def test_jacobian():
    n_viewpoints = 3
    n_points = 4

    points = 10 * unit_uniform((n_points, 3))
    omegas = np.pi * unit_uniform((n_viewpoints, 3))
    translations = 10 * unit_uniform((n_viewpoints, 3))
    poses = to_poses(omegas, translations)

    dpoints = 0.01 * unit_uniform(points.shape)
    domegas = 0.001 * unit_uniform(omegas.shape)
    dtranslations = 0.01 * unit_uniform(translations.shape)
    dposes = to_poses(domegas, dtranslations)

    # assume that all points are visible
    mask = np.ones((n_viewpoints, n_points))
    viewpoint_indices, point_indices = np.where(mask)

    projection = Projection(viewpoint_indices, point_indices)
    A, B = projection.jacobians(poses, points)

    Q = projection.compute

    # test sign(Q(a + da, b) - Q(a, b)) == sign(A * da)
    # where A = dQ / da
    dx_true = Q(poses + dposes, points) - Q(poses, points)
    for index, j in enumerate(viewpoint_indices):
        dx_pred = A[index].dot(dposes[j])
        assert_array_equal(np.sign(dx_true[index]), np.sign(dx_pred))

    # test sign(Q(a, b + db) - Q(a, b)) == sign(B * db)
    # where B = dQ / db
    dx_true = Q(poses, points + dpoints) - Q(poses, points)
    for index, i in enumerate(point_indices):
        dx_pred = B[index].dot(dpoints[i])
        assert_array_equal(np.sign(dx_true[index]), np.sign(dx_pred))


def test_converter():
    from vitamine.pose import Pose

    # index_map = {viewpoint : {keypoint_index: point_index}}
    index_map = {
        0: {1: 3, 3: 5, 4: 2, 5: 1},
        1: {0: 2, 4: 1, 5: 5, 6: 4},
        2: {0: 3, 1: 2, 4: 1}
    }

    viewpoints = [0, 2]

    keypoints_list = [
        np.random.randint(0, 100, (6, 2)),
        np.random.randint(0, 100, (8, 2)),
        np.random.randint(0, 100, (5, 2))
    ]

    omegas = np.random.uniform(-1, 1, (3, 3))
    translations = np.random.uniform(-10, 10, (3, 3))
    poses = [Pose(omega, t) for omega, t in zip(omegas, translations)]
    points = np.random.uniform(-10, 10, (10, 3))

    converter = IndexConverter()
    for viewpoint in viewpoints:
        keypoints = keypoints_list[viewpoint]
        for keypoint_index, point_index in index_map[viewpoint].items():
            converter.add(viewpoint, point_index,
                          poses[viewpoint], points[point_index],
                          keypoints[keypoint_index])

    viewpoint_indices, point_indices, keypoints = converter.export_projection()

    assert_array_equal(viewpoint_indices, [0, 0, 0, 0, 1, 1, 1])
    # point map
    # 3 -> 0
    # 5 -> 1
    # 2 -> 2
    # 1 -> 3
    assert_array_equal(point_indices, [0, 1, 2, 3, 0, 2, 3])
    keypoints0, keypoints1, keypoints2 = keypoints_list
    assert_array_equal(
        keypoints,
        np.array([
            keypoints0[1], keypoints0[3], keypoints0[4], keypoints0[5],
            keypoints2[0], keypoints2[1], keypoints2[4]
        ])
    )

    poses_, points_ = converter.export_pose_points()
    assert(len(poses_) == 2)
    assert(poses_[0] == poses[0])
    assert(poses_[1] == poses[2])

    assert_array_almost_equal(
        points_,
        np.array([points[3], points[5], points[2], points[1]])
    )


def add_noise(array, scale):
    return array + scale * unit_uniform(array.shape)


def test_local_bundle_adjustment():
    def error(keypoints1, keypoints2):
        return np.power(keypoints1 - keypoints2, 2).sum()

    def run(omegas1, translations1, points1):
        keypoints1 = projection.compute(
            to_poses(omegas1, translations1), points1
        )

        # refine parameters
        omegas2, translations2, points2 = local_ba.compute(
            omegas1, translations1, points1)

        keypoints2 = projection.compute(
            to_poses(omegas2, translations2), points2
        )

        # error shoud be decreased after bundle adjustment
        E1 = error(keypoints1, keypoints_true)
        E2 = error(keypoints2, keypoints_true)

        if np.isclose(E1, E2):
            # nothing updated
            assert_array_equal(omegas1, omegas2)
            assert_array_equal(translations1, translations2)
            assert_array_equal(points1, points2)
            return

        assert(E2 < E1)


    mask = np.array([
        [0, 1, 1, 1, 1, 0],  #      x_01 x_02 x_03 x_04 x_05
        [1, 1, 1, 1, 0, 1],  # x_10      x_12           x_15
        [1, 0, 1, 1, 1, 1],  #           x_22      x_24 x_25
        [1, 1, 1, 1, 1, 1],  #      x_31 x_32 x_33 x_34 x_35
        [1, 1, 1, 1, 1, 1]   #           x_42 x_43
    ], dtype=np.bool)

    n_points, n_viewpoints = mask.shape
    point_indices, viewpoint_indices = np.where(mask)

    projection = Projection(viewpoint_indices, point_indices)

    omegas_true = np.pi * unit_uniform((n_viewpoints, 3))
    translations_true = unit_uniform((n_viewpoints, 3))
    points_true = unit_uniform((n_points, 3))

    keypoints_true = projection.compute(
        to_poses(omegas_true, translations_true), points_true
    )

    local_ba = LocalBundleAdjustment(viewpoint_indices, point_indices,
                                     keypoints_true)

    omegas_noisy = add_noise(omegas_true, 0.01 * np.pi)
    translations_noisy = add_noise(translations_true, 0.01)
    points_noisy = add_noise(points_true, 0.01)

    # check BA can refine point / pose parameters for each case
    # if only omegas are noisy
    run(omegas_noisy, translations_true, points_true)
    # if only translations are noisy
    run(omegas_true, translations_noisy, points_true)
    # if only points are noisy
    run(omegas_true, translations_true, points_noisy)
    # if all parameters are noisy
    run(omegas_noisy, translations_noisy, points_noisy)