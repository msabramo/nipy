""" Testing non-linear least squares model
"""

import numpy as np

from nipy.algorithms.statistics import nlsmodel

from numpy.testing import (assert_array_almost_equal,
                           assert_array_equal)

from nose.tools import assert_true, assert_equal, assert_raises

def test_nlsmodel():
    def f(x, theta):
        a, b = theta
        _x = x
        return a * np.exp(-b * _x)

    def grad(x, theta):
        a, b = theta
        value = np.zeros((2, x.shape[0]))
        _x = x
        value[0] = np.exp(-b * _x)
        value[1] = -a * b * np.exp(-b * _x)
        return value.T

    X = np.linspace(0,1,101)
    Y = np.exp(-2 * X) * 3 + np.random.standard_normal(X.shape) * 0.1

    niter = 10
    model = nlsmodel.NLSModel(Y=Y,
                              design=X,
                              f=f,
                              grad=grad,
                              theta=np.array([3, -2.]),
                              niter=niter)

    for iteration in model:
        model.next()

    a, b = model.theta
