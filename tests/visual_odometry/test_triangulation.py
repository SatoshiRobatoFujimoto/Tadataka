from autograd import numpy as np
from numpy.testing import assert_array_almost_equal, assert_array_equal

from vitamine.camera import CameraParameters
from vitamine.dataset.observations import (
    generate_observations, generate_translations)
from vitamine.keypoints import Matcher
from vitamine.projection import PerspectiveProjection
from vitamine.visual_odometry.triangulation import (
    triangulation, copy_triangulated)
from vitamine.pose import Pose
from vitamine.rigid_transform import transform
from vitamine.so3 import rodrigues
from vitamine.utils import random_binary, break_other_than
from vitamine.visual_odometry.point import Points
from vitamine.visual_odometry.keypoint import LocalFeatures
from tests.data import dummy_points as points_true


matcher = Matcher(enable_ransac=False, enable_transfer_detection=False)

camera_parameters = CameraParameters(focal_length=[1, 1], offset=[0, 0])
projection = PerspectiveProjection(camera_parameters)


omegas = np.array([
    [0, 0, 0],
    [0, np.pi / 2, 0],
    [np.pi / 2, 0, 0],
    [0, np.pi / 4, 0],
    [0, -np.pi / 4, 0],
    [-np.pi / 4, np.pi / 4, 0],
    [0, np.pi / 8, -np.pi / 4]
])

rotations = rodrigues(omegas)
translations = generate_translations(rotations, points_true)
keypoints_true, positive_depth_mask = generate_observations(
    rotations, translations, points_true, projection
)

# generate dummy descriptors
# allocate sufficient lengths of descriptors for redundancy
descriptors = random_binary((len(points_true), 1024))


descriptors = random_binary((14, 1024))


def test_copy_triangulated():
    descriptors0 = break_other_than(descriptors,
                                    [0, 2, 4, 5, 6, 7, 9, 10, 11, 12, 13])
    descriptors1 = break_other_than(descriptors,
                                    [0, 1, 2, 4, 6, 7, 8, 10, 11, 12, 13])
    descriptors2 = break_other_than(descriptors,
                                    [1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
    # point_indices   0  1  2  3  4   5   6   7   8
    # matches01.T = [[0, 2, 4, 6, 7, 10, 11, 12, 13],
    #                [0, 2, 4, 6, 7, 10, 11, 12, 13]]
    #
    # point_indices   2  8  3  4  9   5   6   7
    # matches02.T = [[4, 5, 6, 7, 9, 10, 11, 12],
    #                [4, 5, 6, 7, 9, 10, 11, 12]]
    lf0 = LocalFeatures(keypoints_true[0], descriptors0)
    lf1 = LocalFeatures(keypoints_true[1], descriptors1)
    lf2 = LocalFeatures(keypoints_true[2], descriptors2)
    lf1.point_indices = np.array(
        [0, -1, 1, -1, 2, -1, 3, 4, -1, -1, 5, 6, 7, 8]
    )
    lf2.point_indices = np.array(
        [-1, -1, -1, -1, 2, 8, 3, 4, -1, 9, 5, 6, 7, -1]
    )

    copy_triangulated(matcher, [lf1, lf2], lf0)
    assert_array_equal(lf0.point_indices,
                       [0, -1, 1, -1, 2, 8, 3, 4, -1, 9, 5, 6, 7, 8])


def test_triangulation():
    pose0 = Pose(omegas[0], translations[0])
    pose1 = Pose(omegas[1], translations[1])
    pose2 = Pose(omegas[2], translations[2])
    pose3 = Pose(omegas[3], translations[3])
    pose4 = Pose(omegas[4], translations[4])

    def case1():
        # test the case that lf1, lf2, lf3 are already observed and lf0 is added
        # as a new keyframe
        descriptors0 = break_other_than(descriptors,
                                        [0, 1, 4, 5, 7, 8, 9, 10, 11, 12, 13])
        # point_indices   0  1  2  3  4   5   6
        # matches01.T = [[0, 1, 4, 7, 9, 12, 13],
        #                [0, 1, 4, 7, 9, 12, 13]]
        descriptors1 = break_other_than(descriptors,
                                        [0, 1, 2, 3, 4, 7, 9, 12, 13])
        # point_indices   0  1  2     3  4       5   6   existing
        # point_indices            7         8           newly triangulated
        # matches02.T = [[0, 1, 4, 5, 7, 9, 11, 12, 13],
        #                [0, 1, 4, 5, 7, 9, 11, 12, 13]]
        descriptors2 = break_other_than(descriptors,
                                        [0, 1, 4, 5, 7, 9, 11, 12, 13])
        # point_indices   0  1  7  3  4       6   existing
        # point_indices                   9       newly triangulated
        # matches03.T = [[0, 1, 5, 7, 9, 10, 13],
        #                [0, 1, 5, 7, 9, 10, 13]]
        descriptors3 = break_other_than(descriptors,
                                        [0, 1, 2, 5, 7, 9, 10, 13])

        # point_indices   0  1  2  3  4   9   6   existing
        # matches04.T = [[0, 1, 4, 7, 9, 10, 13],
        #                [0, 1, 4, 7, 9, 10, 13]]

        descriptors4 = break_other_than(descriptors,
                                        [0, 1, 4, 7, 9, 10, 13])

        lf0 = LocalFeatures(keypoints_true[0], descriptors0)
        lf1 = LocalFeatures(keypoints_true[1], descriptors1)
        lf2 = LocalFeatures(keypoints_true[2], descriptors2)
        lf3 = LocalFeatures(keypoints_true[3], descriptors3)
        lf4 = LocalFeatures(keypoints_true[4], descriptors4)

        points = Points()
        triangulation(matcher, points,
                      [pose1, pose2, pose3, pose4],
                      [lf1, lf2, lf3, lf4],
                      pose0, lf0)
        assert_array_equal(lf0.point_indices,
                           [0, 1, -1, -1, 2, 7, -1, 3, -1, 4, 9, 8, 5, 6])
        assert_array_equal(lf1.point_indices,
                           [0, 1, -1, -1, 2, -1, -1, 3, -1, 4, -1, -1, 5, 6])
        assert_array_equal(lf2.point_indices,
                           [0, 1, -1, -1, 2, 7, -1, 3, -1, 4, -1, 8, 5, 6])
        assert_array_equal(lf3.point_indices,
                           [0, 1, -1, -1, -1, 7, -1, 3, -1, 4, 9, -1, -1, 6])
        assert_array_equal(lf4.point_indices,
                           [0, 1, -1, -1, 2, -1, -1, 3, -1, 4, 9, -1, -1, 6])


        point_indices0 = lf0.point_indices[lf0.is_triangulated]
        point_indices1 = lf1.point_indices[lf1.is_triangulated]
        point_indices2 = lf2.point_indices[lf2.is_triangulated]
        point_indices3 = lf3.point_indices[lf3.is_triangulated]
        P0 = transform(pose0.R, pose0.t, points.get(point_indices0))
        P1 = transform(pose1.R, pose1.t, points.get(point_indices1))
        P2 = transform(pose2.R, pose2.t, points.get(point_indices2))
        P3 = transform(pose3.R, pose3.t, points.get(point_indices3))
        assert_array_almost_equal(projection.compute(P0),
                                  keypoints_true[0, lf0.is_triangulated])
        assert_array_almost_equal(projection.compute(P1),
                                  keypoints_true[1, lf1.is_triangulated])
        assert_array_almost_equal(projection.compute(P2),
                                  keypoints_true[2, lf2.is_triangulated])
        assert_array_almost_equal(projection.compute(P3),
                                  keypoints_true[3, lf3.is_triangulated])

    def case2():
        # test the case that lf1, lf2, lf3 are already observed and lf0 is added
        # as a new keyframe
        descriptors0 = break_other_than(descriptors[0:10],
                                        [0, 1, 4, 5, 7, 8, 9])
        # point_indices   0  1  2  3  4
        # matches01.T = [[0, 1, 4, 7, 9],
        #                [0, 1, 4, 7, 9]]
        descriptors1 = break_other_than(descriptors[0:14],
                                        [0, 1, 2, 3, 4, 7, 9, 12, 13])
        # point_indices   0  1  2     3  4   existing
        # point_indices            5         newly triangulated
        # matches02.T = [[0, 1, 4, 5, 7, 9],
        #                [0, 1, 4, 5, 7, 9]]
        descriptors2 = break_other_than(descriptors[0:12],
                                        [0, 1, 4, 5, 7, 9, 11])
        # point_indices   2  3  4            existing
        # matches03.T = [[4, 7, 9],          offset +2
        #                [2, 5, 7]]
        descriptors3 = break_other_than(descriptors[2:13],
                                       # 2  3  4  7  9 11  12
                                        [0, 1, 2, 5, 7, 9, 10])
        keypoints0 = keypoints_true[0, 0:10]
        keypoints1 = keypoints_true[1, 0:14]
        keypoints2 = keypoints_true[2, 0:12]
        keypoints3 = keypoints_true[3, 2:13]
        lf0 = LocalFeatures(keypoints0, descriptors0)
        lf1 = LocalFeatures(keypoints1, descriptors1)
        lf2 = LocalFeatures(keypoints2, descriptors2)
        lf3 = LocalFeatures(keypoints3, descriptors3)
        points = Points()
        triangulation(matcher, points,
                      [pose1, pose2, pose3], [lf1, lf2, lf3], pose0, lf0)
        assert_array_equal(lf0.point_indices,
                           [0, 1, -1, -1, 2, 5, -1, 3, -1, 4])
        assert_array_equal(lf1.point_indices,
                           [0, 1, -1, -1, 2, -1, -1, 3, -1, 4, -1, -1, -1, -1])
        assert_array_equal(lf2.point_indices,
                           [0, 1, -1, -1, 2, 5, -1, 3, -1, 4, -1, -1])
        assert_array_equal(lf3.point_indices,
                           [-1, -1, 2, -1, -1, 3, -1, 4, -1, -1, -1])

        point_indices0 = lf0.point_indices[lf0.is_triangulated]
        point_indices1 = lf1.point_indices[lf1.is_triangulated]
        point_indices2 = lf2.point_indices[lf2.is_triangulated]
        point_indices3 = lf3.point_indices[lf3.is_triangulated]
        P0 = transform(pose0.R, pose0.t, points.get(point_indices0))
        P1 = transform(pose1.R, pose1.t, points.get(point_indices1))
        P2 = transform(pose2.R, pose2.t, points.get(point_indices2))
        P3 = transform(pose3.R, pose3.t, points.get(point_indices3))
        assert_array_almost_equal(projection.compute(P0),
                                  keypoints0[lf0.is_triangulated])
        assert_array_almost_equal(projection.compute(P1),
                                  keypoints1[lf1.is_triangulated])
        assert_array_almost_equal(projection.compute(P2),
                                  keypoints2[lf2.is_triangulated])
        assert_array_almost_equal(projection.compute(P3),
                                  keypoints3[lf3.is_triangulated])

    case1()
    case2()
