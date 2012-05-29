# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
import warnings
import numpy as np

import nibabel as nib

from ...core.api import (CoordinateMap, AffineTransform, CoordinateSystem,
                           lps_output_coordnames, ras_output_coordnames)
from ...core.reference.spaces import (unknown_csm, scanner_csm, aligned_csm,
                                      talairach_csm)

from ..files import load, save
from ..nifti_ref import (nipy2hdr_data, hdr_data2nipy,
                         get_input_cs, get_output_cs)

from nose.tools import assert_equal, assert_true, assert_false, assert_raises
from numpy.testing import assert_almost_equal

from ...testing import anatfile, funcfile


shape = range(1,8)
step = np.arange(1,8)


def setup():
    # Suppress warnings during tests
    warnings.simplefilter("ignore")


def teardown():
    # Clear list of warning filters
    warnings.resetwarnings()


def test_nipy2hdr_data():
    # Go from nipy image to header and data for nifti
    # Header is preserved, copied as necesary
    fimg = load(funcfile)
    data = fimg.get_data()
    hdr = fimg.metadata['header']
    new_hdr, new_data = nipy2hdr_data(fimg)
    assert_false(hdr is new_hdr)
    assert_equal(hdr['slice_duration'], new_hdr['slice_duration'])
    assert_true(data is new_data)


def test_input_cs():
    # Test ability to detect input coordinate system
    # I believe nifti is the only format to specify interesting meanings for the
    # input axes
    for hdr in (nib.Spm2AnalyzeHeader(), nib.Nifti1Header()):
        for shape, names in (((2,), 'i'),
                            ((2,3), 'ij'),
                            ((2,3,4), 'ijk'),
                            ((2,3,4,5), 'ijkl')):
            hdr.set_data_shape(shape)
            assert_equal(get_input_cs(hdr), CoordinateSystem(names, 'voxel'))
    hdr = nib.Nifti1Header()
    # Just confirm that the default leads to no axis renaming
    hdr.set_data_shape((2,3,4))
    hdr.set_dim_info(None, None, None) # the default
    assert_equal(get_input_cs(hdr), CoordinateSystem('ijk', 'voxel'))
    # But now...
    hdr.set_dim_info(freq=1)
    assert_equal(get_input_cs(hdr),
                 CoordinateSystem(('i', 'freq', 'k'), "voxel"))
    hdr.set_dim_info(freq=2)
    assert_equal(get_input_cs(hdr),
                 CoordinateSystem(('i', 'j', 'freq'), "voxel"))
    hdr.set_dim_info(phase=1)
    assert_equal(get_input_cs(hdr),
                 CoordinateSystem(('i', 'phase', 'k'), "voxel"))
    hdr.set_dim_info(freq=1, phase=0, slice=2)
    assert_equal(get_input_cs(hdr),
                 CoordinateSystem(('phase', 'freq', 'slice'), "voxel"))


def test_output_cs():
    # Test return of output coordinate system from header
    # With our current use of nibabel, there is always an xyz output.  But, with
    # nifti, the xform codes can specify one of four known output spaces.
    # But first - length is always 3 until we have more than 3 input dimensions
    cs = unknown_csm(3) # A length 3 xyz output
    hdr = nib.Nifti1Header()
    hdr.set_data_shape((2,))
    assert_equal(get_output_cs(hdr), cs)
    hdr.set_data_shape((2,3))
    assert_equal(get_output_cs(hdr), cs)
    hdr.set_data_shape((2,3,4))
    assert_equal(get_output_cs(hdr), cs)
    # With more than 3 inputs, the output dimensions expand
    hdr.set_data_shape((2,3,4,5))
    assert_equal(get_output_cs(hdr), unknown_csm(4))
    # Now, nifti can change the output labels with xform codes
    hdr['qform_code'] = 1
    assert_equal(get_output_cs(hdr), scanner_csm(4))
    hdr['qform_code'] = 3
    assert_equal(get_output_cs(hdr), talairach_csm(4))
    hdr['sform_code'] = 2
    assert_equal(get_output_cs(hdr), aligned_csm(4))
    hdr['sform_code'] = 0
    assert_equal(get_output_cs(hdr), talairach_csm(4))
