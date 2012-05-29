# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
"""
An implementation of the dimension info as desribed in:

http://nifti.nimh.nih.gov/pub/dist/src/niftilib/nifti1.h

A version of the same file is in the nibabel repisitory at
``doc/source/external/nifti1.h``.

Background
==========

We (nipystas) make an explicit distinction between

* an input coordinate system of an image (the array == voxel coordinates)
* output coordinate system (usually millimeters in some world)
* the mapping between the two.

The collection of these three is the ``coordmap`` attribute of a NIPY image.

There is no constraint that the number of input and output coordinates should be
the same.

We don't specify the units of our output coordinate system, but assume spatial
units are millimeters and time units are seconds.

NIFTI is mostly less explicit, but more constrained.

NIFTI input coordinate system
-----------------------------

NIFTI files can have up to seven voxel dimensions (7 axes in the input
coordinate system).

The first 3 voxel dimensions of a NIFTI file must be spatial but can be in any
order in relationship to directions in mm space (the output coordinate system)

The 4th voxel dimension is assumed to be time.  In particular, if you have some
other meaning for a non-spatial dimension, the NIFTI standard suggests you set
the length of the 4th dimension to be 1, and use the 5th dimension of the image
instead, and set the NIFTI "intent" fields to state the meaning. If the
``intent`` field is set correctly then it should be possible to set meaningful
input coordinate axis names for dimensions > (0, 1, 2).

There's wrinkle to the 4th axis is time story; the ``xyxt_units`` field in the
NIFTI header can specify the 4th dimension units as Hz (frequency),
PPM (concentration) or Radians / second.

NIFTI also has a 'dim_info' header attribute that optionally specifies that 0 or
more of the first three voxel axes are 'frequency', 'phase' or 'slice'.  These
terms refer to 2D MRI acquisition encoding, where 'slice's are collected
sequentially, and the two remaining dimensions arose from frequency and phase
encoding.  The ``dim_info`` fields are often not set.  3D acquisitions don't have
a 'slice' dimension.

NIFTI output coordinate system
------------------------------

In the NIFTI specification, the order of the output coordinates (at least the
first 3) are fixed to be what might be called RAS+, that is ('x=L->R', 'y=P->A',
'z=I->S'). This RAS+ output order is not allowed to change and there is no way of
specifying such a change in the nifti header.

The world in which these RAS+ X, Y, Z axes exist can be one of the recognized
spaces, which are: scanner, aligned (to another file's world space), Talairach,
MNI 152 (aligned to the MNI 152 atlas).

By implication, the 4th output dimension is likely to be seconds (given the 4th
input dimension is likley time), but there's a field ``xyzt_units`` (see above)
that can be used to imply the 4th output dimension is actually frequency,
concentration or angular velocity.

NIFTI input / output mapping
----------------------------

NIFTI stores the relationship between the first 3 (spatial) voxel axes and the
RAS+ coordinates in an *XYZ affine*.  This is a homogenous coordinate affine,
hence 4 by 4 for 3 (spatial) dimensions.

NIFTI also stored "pixel dimensions" in a ``pixdim`` field. This can give you
scaling for individual axes.  We ignore the values of ``pixdim`` for the first 3
axes if we have a full ("sform") affine stored in the header, otherwise they
form part of the affine above.  Later values provide voxel to output calings for
later axes.  The units for the 4th dimension can come from ``xyzt_units`` as
above.

We take the convention that the output coordinate names are ('x=L->R', 'y=P->A',
'z=I->S','t','u','v','w').  The first 3 axes are also named after the output
space ('scanner-x=L->R', 'mni-x=L-R' etc).

What we do about all this
=========================

On saving a NIPY image to NIFTI
-------------------------------

First, we need to create a valid XYZ Affine.  We check if this can be done by
checking if there are recognizable X, Y, Z output axes and corresponding input
(voxel) axes.  This requires the input image to be at least 3D. If we find these
requirements, we reorder the image axes to have XYZ output axes and 3 spatial
input axes first, and get the corresponding XYZ affine.

We check if the XYZ output fits with the the NIFTI named spaces of scanner,
aligned, Talairach, MNI.  If not we raise an error.

If the non-spatial dimensions are not orthogonal to each other, raise an error.

If any of the first three input axes are named ('slice', 'freq', 'phase') set
the ``dim_info`` field accordingly.

Set the ``xyzt_units`` field to indicate millimeters and seconds, if there is a
't' axis, otherwise millimeters and 0 (unknown).

We look to see if we have an *input* axis named 't'. If we do, roll that axis to
be the 4th axis. Take the ``affine[3, -1]`` and put into the ``toffset`` field.
If there's no 't' axis, but there are other non-spatial axes, make a length 1
input axis to indicate this.

If there is an *input* axis named any of frequency-hz', 'concentration-ppm' or
'radians/s' and there is no 't' axis, move the axis to the 4th position and set
``xyz_units``.

Set ``pixdim`` for axes >= 3 using vector length of corresponding affine
columns.

We don't set the intent-related fields for now.

On loading a NIPY image from NIFTI
----------------------------------

Lacking any other information, we take the input coordinate names for
axes 0:7 to be  ('i', 'j', 'k', 't', 'u', 'v', 'w').

If axis 3 (4th) is length 1 and there are more than 4 dimensions to the input
array, then squeeze the 4th dimension and omit 't' above. If ``xyzt_units``
shows 4th axis to be Hz, PPM or radians / second, set the 4th axis name to
'frequency-hz', 'concentration-ppm' or 'radians/s' respectively.

If there's a 't' axis get ``toffset`` and put into affine at position [3, -1].

If ``dim_info`` is set coherently, set input axis names to 'slice', 'freq',
'phase' from ``dim_info``.

Get the output spatial coordinate names from the 'scanner', 'aligned',
'talairach', 'mni' XYZ spaces (see :mod:`nipy.core.reference.spaces`).

We construct the N-D affine by taking the XYZ affine and adding scaling diagonal
elements from ``pixdim``.

Ignore the intent-related fields for now.

"""

import warnings
from copy import copy

import numpy as np

import nibabel as nib
from nibabel.affines import to_matvec

from ..core.reference.coordinate_system import CoordinateSystem as CS
from ..core.reference import spaces as ncrs
from ..core.image.image import rollaxis as img_rollaxis
from ..core.image.image_spaces import as_xyz_affable


XFORM2SPACE = {'scanner': ncrs.scanner_space,
               'aligned': ncrs.aligned_space,
               'talairach': ncrs.talairach_space,
               'mni': ncrs.mni_space}

TIME_LIKE_AXES = ( # name, matcher, units
    ('t', lambda n : n == 't' or n == 'time', 'sec'),
    ('hz', lambda n : n == 'hz' or n == 'frequency-hz', 'hz'),
    ('ppm', lambda n : n == 'ppm' or n == 'concentration-ppm', 'ppm'),
    ('rads', lambda n : n == 'rads' or n == 'radians/s', 'rads'),
)

# Threshold for near-zero affine values
TINY = 1e-5


class NiftiError(Exception):
    pass


def nipy2hdr_data(img, strict=None):
    """ Return header and data to create Nifti image from NIPY `img`

    Parameters
    ----------
    img : object
         An object, usually a NIPY ``Image``,  having attributes `coordmap` and
         `shape`
    strict : bool, optional
        Whether to use strict checking of input image for creating nifti

    Returns
    -------
    header : Nifti1Header
        Nifti header with fields set as for eventual image
    data : array
        data to write to nifti image

    Notes
    -----
    First, we need to create a valid XYZ Affine.  We check if this can be done
    by checking if there are recognizable X, Y, Z output axes and corresponding
    input (voxel) axes.  This requires the input image to be at least 3D. If we
    find these requirements, we reorder the image axes to have XYZ output axes
    and 3 spatial input axes first, and get the corresponding XYZ affine.

    If the non-spatial dimensions are not orthogonal to each other, raise an
    error.

    We check if the XYZ output fits with the the NIFTI named spaces of scanner,
    aligned, Talairach, MNI.  If not we raise an error.

    If any of the first three input axes are named ('slice', 'freq', 'phase')
    set the ``dim_info`` field accordingly.

    Set the ``xyzt_units`` field to indicate millimeters and seconds, if there
    is a 't' axis, otherwise millimeters and 0 (unknown).

    We look to see if we have an output axis named 't'. If we do, roll that axis
    to be the 4th axis. Take the ``affine[3, -1]`` and put into the ``toffset``
    field.  If there's no 't' axis, but there are other non-spatial axes, make a
    length 1 input axis to indicate this.

    If there is an axis named any of frequency-hz', 'concentration-ppm' or
    'radians/s' and there is no 't' axis, move the axis to the 4th position and
    set ``xyz_units``.

    Set ``pixdim`` for axes >= 3 using vector length of corresponding affine
    columns.

    We don't set the intent-related fields for now.
    """
    strict_none = strict is None
    if strict_none:
        warnings.warn('Default `strict` currently False; this will change to '
                      'True in a future version of nipy',
                      FutureWarning,
                      stacklevel = 2)
        strict = False
    known_names = ncrs.known_names
    if not strict:
        known_names = copy(known_names)
        for c in 'xyz':
            known_names[c] = c
    img = as_xyz_affable(img, known_names)
    coordmap = img.coordmap
    # Get useful information from old header
    in_hdr = img.metadata.get('header', None)
    hdr = nib.Nifti1Header.from_header(in_hdr)
    # Remaining axes orthogonal?
    rzs, trans = to_matvec(coordmap.affine)
    if (not np.allclose(rzs[3:, :3], 0) or
        not np.allclose(rzs[:3, 3:], 0)):
        raise NiftiError('Non space axes not orthogonal to space')
    # And to each other?
    nsp_affine = rzs[3:,3:]
    nsp_nzs = np.abs(nsp_affine) > TINY
    n_in_col = np.sum(nsp_nzs, axis=0)
    n_in_row = np.sum(nsp_nzs, axis=1)
    if np.any(n_in_col > 1) or np.any(n_in_row > 1):
        raise NiftiError('Non space axes not orthogonal to each other')
    # Affine seems OK, check for space
    xyz_affine = ncrs.xyz_affine(coordmap, known_names)
    spatial_output_names = coordmap.function_range.coord_names[:3]
    out_space = CS(spatial_output_names)
    hdr = nib.Nifti1Header()
    for name, space in XFORM2SPACE.items():
        if out_space in space:
            hdr.set_sform(xyz_affine, name)
            hdr.set_qform(xyz_affine, name)
            break
    else:
        if not strict and spatial_output_names == ('x', 'y', 'z'):
            warnings.warn('Default `strict` currently False; '
                          'this will change to True in a future version of '
                          'nipy; output names of "x", "y", "z" will raise '
                          'an error.  Please use canonical output names from '
                          'nipy.core.reference.spaces',
                          FutureWarning,
                          stacklevel = 2)
            hdr.set_sform(xyz_affine, 'scanner')
            hdr.set_qform(xyz_affine, 'scanner')
        else:
            raise ncrs.NiftiError('Image world not a Nifti world')
    # Set dim_info
    # Use list() to get .index method for python < 2.6
    input_names = list(coordmap.function_domain.coord_names)
    spatial_names = input_names[:3]
    dim_infos = []
    for fps in 'freq', 'phase', 'slice':
        dim_infos.append(
            spatial_names.index(fps) if fps in spatial_names else None)
    hdr.set_dim_info(*dim_infos)
    # Set units without knowing time
    hdr.set_xyzt_units(xyz='mm')
    # Done if we only have 3 input dimensions
    non_space_inames = input_names[3:]
    non_space_onames = coordmap.function_domain.coord_names[3:]
    if len(non_space_inames) == 0:
        return hdr, img.get_data()
    # Look for time and time-related axes in input and then maybe output names
    for name, matcher, units in TIME_LIKE_AXES:
        for in_ns_no, in_ax_name in enumerate(non_space_inames):
            if matcher(in_ax_name):
                break
            continue
        # Make sure this axis is first non-space axis
        if in_ns_no != 0:
            img = img_rollaxis(img, in_ns_no + 3, 3)
        # xyzt_units
        hdr.set_xyzt_units(xyz='mm', t=units)
        # If this is time, set toffset
        if name == 't':
            # Which output axis corresponds?
            for out_ns_no, out_ax_name in enumerate(non_space_onames):
                if matcher(out_ax_name):
                    break
                corr_row = np.nonzero(nzs[in_ns_no])[0]
                if len(corr_row) > 1 or not np.all(corr_row == out_ns_no):
                    raise NiftiError('Time input and output do not match')
                hdr['toffset'] = trans[out_ns_no]
        data = img.get_data()
        break
    else: # no time-like axis
        # add new 1-length axis
        data = img.get_data()[:, :, :, None, ...]
    # Our axes might have changed
    rzs, trans = to_matvec(img.coordmap.affine)
    hdr['pixdim'][3:] = np.sqrt(np.sum(rzs[3:, 3:] ** 2, axis=0))
    return hdr, data


def hdr_data2nipy(header, data):
    """ Return parameters to create NIPY image from nifti `header`

    Parameters
    ----------
    header : Nifti1Header
        Nifti header with fields set as for eventual image

    Returns
    -------
    transposes : None or sequence
        New ordering for `img` array axes (to be applied before `reshapes`)
    reshapes : None or sequence
        Reshaping for `img` array axes (to be applied after `transposes`
    coordmap : AffineTransform
        Coordinate map expressing mapping image axes (after application of
        `reshapes` and `tranposes`) to world coordinates.
    """
    pass


def get_input_cs(hdr):
    """ Get input (function_domain) coordinate system from `hdr`

    Look at the header `hdr` to see if we have information about the image axis
    names.  So far this is ony true of the nifti header, which can use the
    ``dim_info`` field for this.  If we can't find any information, use the
    default names from 'ijklmnop'

    Parameters
    ----------
    hdr : object
        header object, having at least a ``get_data_shape`` method

    Returns
    -------
    cs : ``CoordinateSystem``
        Input (function_domain) Coordinate system

    Example
    -------
    >>> class C(object):
    ...     def get_data_shape(self):
    ...         return (2,3)
    ...
    >>> hdr = C()
    >>> get_input_cs(hdr)
    CoordinateSystem(coord_names=('i', 'j'), name='voxel', coord_dtype=float64)
    """
    ndim = len(hdr.get_data_shape())
    all_names = list('ijklmno')
    try:
        freq, phase, slice = hdr.get_dim_info()
    except AttributeError:
        pass
    else: # Nifti - maybe we have named axes
        if not freq is None:
            all_names[freq] = 'freq'
        if not phase is None:
            all_names[phase] = 'phase'
        if not slice is None:
            all_names[slice] = 'slice'
    return CS(all_names[:ndim], 'voxel')


def get_output_cs(hdr):
    """ Calculate output (function range) coordinate system from `hdr`

    With our current use of nibabel for image loading, there is always an xyz
    output, because nibabel images always have 4x4 xyz affines.  So, the output
    coordinate system has a least 3 coordinates (those for x, y, z), regardless
    of the array shape implied by `hdr`.  If `hdr` implies a larger array shape
    N (where N>3), then the output coordinate system will be length N.

    Nifti also allows us to specify one of 4 named output spaces (scanner,
    aligned, talairach and mni).

    Parameters
    ----------
    hdr : object
        header object, having at least a ``get_data_shape`` method

    Returns
    -------
    cs : ``CoordinateSystem``
        Input (function_domain) Coordinate system

    Example
    -------
    >>> class C(object):
    ...     def get_data_shape(self):
    ...         return (2,3)
    ...
    >>> hdr = C()
    >>> get_output_cs(hdr)
    CoordinateSystem(coord_names=('unknown-x=L->R', 'unknown-y=P->A', 'unknown-z=I->S'), name='unknown', coord_dtype=float64)
    """
    # Affines from nibabel always have 3 dimensions of output
    ndim = max((len(hdr.get_data_shape()), 3))
    try:
        label = hdr.get_value_label('sform_code')
    except AttributeError: # not nifti
        return ncrs.unknown_csm(ndim)
    if label == 'unknown':
        label = hdr.get_value_label('qform_code')
    space = XFORM2SPACE.get(label, ncrs.unknown_space)
    return space.to_coordsys_maker('tuvw')(ndim)
