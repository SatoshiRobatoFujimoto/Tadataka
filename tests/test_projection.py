import numpy as np
from numpy.testing import assert_array_almost_equal

from tadataka.projection import pi


def test_pi():
    P = np.array([
        [0, 0, 0],
        [1, 4, 2],
        [-1, 3, 5],
    ], dtype=np.float64)

    assert_array_almost_equal(
        pi(P),
        [[0., 0.], [0.5, 2.0], [-0.2, 0.6]]
    )

    assert_array_almost_equal(pi(np.array([0., 0., 0.])), [0, 0])
    assert_array_almost_equal(pi(np.array([3., 5., 5.])), [0.6, 1.0])