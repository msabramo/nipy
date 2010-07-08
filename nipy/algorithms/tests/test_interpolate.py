""" Testing interpolation routines
"""

import numpy as np

from nipy.algorithms.interpolation import ImageInterpolator
from nipy.core.image import image

from nose.tools import assert_true, assert_false, \
     assert_equal, assert_raises

from numpy.testing import assert_array_equal, assert_array_almost_equal

from nipy.testing import parametric

@parametric
def test_interpolator():
    arr = np.arange(24).reshape(2,3,4)
    img = image.fromarray(arr, 'ijk', 'xyz')
    for order in range(4):
        interp = ImageInterpolator(img, order=order)
        yield assert_array_almost_equal(interp.evaluate([1, 2, 3]), 23)
    # test whether using mmap makes a difference
    interp = ImageInterpolator(img, use_mmap=True)
    yield assert_array_almost_equal(interp.evaluate([1, 2, 3]), 23)
    val = interp.evaluate([1, 2, 3])
    yield assert_equal(val.dtype, np.float)
    # try preserving dtype
    interp = ImageInterpolator(img, preserve_dtype=True)
    val = interp.evaluate([1, 2, 3])
    yield assert_equal(val.dtype, arr.dtype)
    interp = ImageInterpolator(img, use_mmap=True, preserve_dtype=True)
    val = interp.evaluate([1, 2, 3])
    yield assert_equal(val.dtype, arr.dtype)
