from autograd import numpy as np
from numpy.testing import assert_equal

from vitamine.optimization.robustifiers import SquaredRobustifier
from vitamine.optimization.errors import SumRobustifiedNormError
from vitamine.optimization.transformers import BaseTransformer
from vitamine.optimization.optimizers import BaseOptimizer
from vitamine.optimization.residuals import BaseResidual


class Transformer(BaseTransformer):
    def compute(self, params):
        return params


def test_calc_error():
    y = np.array([
        [1, 2],
        [1, 0],
        [-1, 3],
        [2, 2]
    ])
    x = np.array([
        [-1, -3],
        [1, -1],
        [-1, 3],
        [0, 0]
    ])

    transformer = Transformer()
    robustifier = SquaredRobustifier()
    error = SumRobustifiedNormError(robustifier)
    residual = BaseResidual(y, transformer)
    optimizer = BaseOptimizer(None, residual, error)
    assert_equal(optimizer.calc_error(x), 38)