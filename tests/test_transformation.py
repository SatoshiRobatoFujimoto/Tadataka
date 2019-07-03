from autograd import numpy as np
from numpy.testing import assert_array_equal

from rigid.transformation import transform_each


def test_transform_each():
    points = np.array([
        [1, 2, 5],
        [4, -2, 3],
        [0, 0, 6]
    ])

    rotations = np.array([
        [[1, 0, 0],
         [0, 0, -1],
         [0, 1, 0]],
        [[0, 0, -1],
         [0, 1, 0],
         [1, 0, 0]]
    ])
    translations = np.array([
        [1, 2, 3],
        [4, 5, 6]
    ])

    expected = np.array([
        [[2, -3, 5],   # [ 1, -5,  2] + [ 1,  2,  3]
         [5, -1, 1],   # [ 4, -3, -2] + [ 1,  2,  3]
         [1, -4, 3]],  # [ 0, -6,  0] + [ 1,  2,  3]
        [[-1, 7, 7],   # [-5,  2,  1] + [ 4,  5,  6]
         [1, 3, 10],   # [-3, -2,  4] + [ 4,  5,  6]
         [-2, 5, 6]]   # [-6,  0,  0] + [ 4,  5,  6]
    ])

    assert_array_equal(transform_each(rotations, translations, points),
                       expected)
