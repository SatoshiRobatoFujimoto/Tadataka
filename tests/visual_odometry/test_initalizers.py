import pytest

from autograd import numpy as np
from numpy.testing import assert_equal

from vitamine.visual_odometry.initializers import (
    Initializer, select_next_viewpoint)



def test_select_next_viewpoint():
    points = np.array([
        [1, 2, 3],
        [4, 5, 6],
        [np.nan, np.nan, np.nan]
    ])

    keypoints = np.array([
        [[np.nan, np.nan],
         [np.nan, np.nan],
         [np.nan, np.nan]],
        [[1, 2],
         [3, 4],
         [np.nan, np.nan]],
        [[1, 2],
         [3, 4],
         [np.nan, np.nan]],
        [[1, 2],
         [np.nan, np.nan],
         [3, 4]],
    ],
    dtype=np.float64)

    used_viewpoints = set([1])
    assert_equal(select_next_viewpoint(points, keypoints, used_viewpoints), 2)


    with pytest.raises(ValueError):
        select_next_viewpoint(points, keypoints,
                              used_viewpoints=set([0, 1, 2, 3]))