""" Testing coordinate map defined spaces
"""

import numpy as np

from ...image.image import Image
from ..coordinate_system import CoordinateSystem as CS, CoordSysMakerError
from ..coordinate_map import AffineTransform, CoordinateMap
from ...transforms.affines import from_matrix_vector
from ..spaces import (vox2mni, vox2scanner, vox2talairach, vox2unknown,
                      vox2aligned, xyz_affine, xyz_order, SpaceTypeError,
                      AxesError, AffineError, XYZSpace, known_space,
                      known_spaces)

from numpy.testing import (assert_array_almost_equal,
                           assert_array_equal)

from nose.tools import (assert_true, assert_false, assert_equal, assert_raises,
                        assert_not_equal)

VARS = {}


def setup():
    d_names = list('ijkl')
    xyzs = 'x=L->R', 'y=P->A', 'z=I->S'
    mni_xyzs = ['mni-' + suff for suff in xyzs]
    scanner_xyzs = ['scanner-' + suff for suff in xyzs]
    unknown_xyzs = ['unknown-' + suff for suff in xyzs]
    aligned_xyzs = ['aligned-' + suff for suff in xyzs]
    talairach_xyzs = ['talairach-' + suff for suff in xyzs]
    r_names = mni_xyzs + ['t']
    d_cs_r3 = CS(d_names[:3], 'array')
    d_cs_r4 = CS(d_names[:4], 'array')
    r_cs_r3 = CS(r_names[:3], 'mni')
    r_cs_r4 = CS(r_names[:4], 'mni')
    VARS.update(locals())


def test_xyz_space():
    # Space objects
    sp = XYZSpace('hijo')
    assert_equal(sp.name, 'hijo')
    exp_labels = ['hijo-' + L for L in 'x=L->R', 'y=P->A', 'z=I->S']
    exp_map = dict(zip('xyz', exp_labels))
    assert_equal([sp.x, sp.y, sp.z], exp_labels)
    assert_equal(sp.as_tuple(), tuple(exp_labels))
    assert_equal(sp.as_map(), exp_map)
    known = {}
    sp.register_to(known)
    assert_equal(known, dict(zip(exp_labels, 'xyz')))
    # Coordinate system making, and __contains__ tests
    csm = sp.to_coordsys_maker()
    cs = csm(2)
    assert_equal(cs, CS(exp_labels[:2], 'hijo'))
    # This is only 2 dimensions, not fully in space
    assert_false(cs in sp)
    cs = csm(3)
    assert_equal(cs, CS(exp_labels, 'hijo'))
    # We now have all 3, this in in the space
    assert_true(cs in sp)
    # More dimensions than default, error
    assert_raises(CoordSysMakerError, csm, 4)
    # But we can pass in names for further dimensions
    csm = sp.to_coordsys_maker('tuv')
    cs = csm(6)
    assert_equal(cs, CS(exp_labels + list('tuv'), 'hijo'))
    # These are also in the space, because they contain xyz
    assert_true(cs in sp)
    # But, to be in the space, x,y,z have to be first and in the right order
    cs = CS(exp_labels, 'hijo')
    assert_true(cs in sp)
    cs = CS(exp_labels[::-1], 'hijo')
    assert_false(cs in sp)
    cs = CS(['t'] + exp_labels, 'hijo')
    assert_false(cs in sp)
    # The coordinate system name doesn't matter though
    cs = CS(exp_labels, 'hija')
    assert_true(cs in sp)
    # Images, and coordinate maps, also work
    cmap = AffineTransform('ijk', cs, np.eye(4))
    assert_true(cmap in sp)
    img = Image(np.zeros((2,3,4)), cmap)
    assert_true(img in sp)
    # equality
    assert_equal(XYZSpace('hijo'), XYZSpace('hijo'))
    assert_not_equal(XYZSpace('hijo'), XYZSpace('hija'))


def test_known_space():
    # Known space utility routine
    for sp in known_spaces:
        cs = sp.to_coordsys_maker()(3)
        assert_equal(known_space(cs), sp)
    cs = CS('xyz')
    assert_equal(known_space(cs), None)
    sp0 = XYZSpace('hijo')
    sp1 = XYZSpace('hija')
    custom_spaces = (sp0, sp1)
    for sp in custom_spaces:
        cs = sp.to_coordsys_maker()(3)
        assert_equal(known_space(cs, custom_spaces), sp)


def test_image_creation():
    # 3D image
    arr = np.arange(24).reshape(2,3,4)
    aff = np.diag([2,3,4,1])
    img = Image(arr, vox2mni(aff))
    assert_equal(img.shape, (2,3,4))
    assert_array_equal(img.affine, aff)
    assert_array_equal(img.coordmap,
                       AffineTransform(VARS['d_cs_r3'], VARS['r_cs_r3'], aff))
    # 4D image
    arr = np.arange(24).reshape(2,3,4,1)
    img = Image(arr, vox2mni(aff, 7))
    exp_aff = np.diag([2,3,4,7,1])
    assert_equal(img.shape, (2,3,4,1))
    exp_cmap = AffineTransform(VARS['d_cs_r4'], VARS['r_cs_r4'], exp_aff)
    assert_equal(img.coordmap, exp_cmap)


def test_default_makers():
    # Tests that the makers make expected coordinate maps
    for csm, r_names, r_name in (
        (vox2scanner, VARS['scanner_xyzs'] + ['t'], 'scanner'),
        (vox2unknown, VARS['unknown_xyzs'] + ['t'], 'unknown'),
        (vox2aligned, VARS['aligned_xyzs'] + ['t'], 'aligned'),
        (vox2mni, VARS['mni_xyzs'] + ['t'], 'mni'),
        (vox2talairach, VARS['talairach_xyzs'] + ['t'], 'talairach')):
        for i in range(1,5):
            dom_cs = CS('ijkl'[:i], 'array')
            ran_cs = CS(r_names[:i], r_name)
            aff = np.diag(range(i) + [1])
            assert_equal(csm(aff), AffineTransform(dom_cs, ran_cs, aff))


def test_xyz_affine():
    # Getting an xyz affine from coordmaps
    affine = from_matrix_vector(np.arange(9).reshape((3,3)), [15,16,17])
    cmap = AffineTransform(VARS['d_cs_r3'], VARS['r_cs_r3'], affine)
    assert_array_equal(xyz_affine(cmap), affine)
    # Affine always reordered in xyz order
    assert_array_equal(xyz_affine(cmap.reordered_range([2,0,1])), affine)
    assert_array_equal(xyz_affine(cmap.reordered_range([2,1,0])), affine)
    assert_array_equal(xyz_affine(cmap.reordered_range([1,2,0])), affine)
    assert_array_equal(xyz_affine(cmap.reordered_range([1,0,2])), affine)
    assert_array_equal(xyz_affine(cmap.reordered_range([0,2,1])), affine)
    # 5x5 affine is shrunk
    rzs = np.c_[np.arange(12).reshape((4,3)), [0,0,0,12]]
    aff55 = from_matrix_vector(rzs, [15,16,17,18])
    cmap = AffineTransform(VARS['d_cs_r4'], VARS['r_cs_r4'], aff55)
    assert_array_equal(xyz_affine(cmap), affine)
    # Affine always reordered in xyz order
    assert_array_equal(xyz_affine(cmap.reordered_range([3,2,1,0])), affine)
    assert_array_equal(xyz_affine(cmap.reordered_range([2,0,1,3])), affine)
    # xyzs must be orthogonal to dropped axis
    for i in range(3):
        aff = aff55.copy()
        aff[i,3] = 1
        cmap = AffineTransform(VARS['d_cs_r4'], VARS['r_cs_r4'], aff)
        assert_raises(AffineError, xyz_affine, cmap)
        # And if reordered
        assert_raises(AffineError, xyz_affine, cmap.reordered_range([2,0,1,3]))
    # Non-square goes to square
    rzs = np.arange(12).reshape((4,3))
    aff54 = from_matrix_vector(rzs, [15,16,17,18])
    cmap = AffineTransform(VARS['d_cs_r3'], VARS['r_cs_r4'], aff54)
    assert_array_equal(xyz_affine(cmap), affine)
    rzs = np.c_[np.arange(12).reshape((4,3)), np.zeros((4,3))]
    aff57 = from_matrix_vector(rzs, [15,16,17,18])
    d_cs_r6 = CS('ijklmn', 'array')
    cmap = AffineTransform(d_cs_r6, VARS['r_cs_r4'], aff57)
    assert_array_equal(xyz_affine(cmap), affine)
    # Non-affine raises SpaceTypeError
    cmap_cmap = CoordinateMap(VARS['d_cs_r4'], VARS['r_cs_r4'], lambda x:x*3)
    assert_raises(SpaceTypeError, xyz_affine, cmap_cmap)
    # Not enough dimensions - SpaceTypeError
    d_cs_r2 = CS('ij', 'array')
    r_cs_r2 = CS(VARS['r_names'][:2], 'mni')
    cmap = AffineTransform(d_cs_r2, r_cs_r2,
                           np.array([[2,0,10],[0,3,11],[0,0,1]]))
    assert_raises(AxesError, xyz_affine, cmap)
    # Any dimensions not spatial, AxesError
    r_cs = CS(('mni-x', 'mni-y', 'mni-q'), 'mni')
    cmap = AffineTransform(VARS['d_cs_r3'],r_cs, affine)
    assert_raises(AxesError, xyz_affine, cmap)
    # Can pass in own validator
    my_valtor = dict(blind='x', leading='y', ditch='z')
    r_cs = CS(('blind', 'leading', 'ditch'), 'fall')
    cmap = AffineTransform(VARS['d_cs_r3'],r_cs, affine)
    assert_raises(AxesError, xyz_affine, cmap)
    assert_array_equal(xyz_affine(cmap, my_valtor), affine)


def test_xyz_order():
    # Getting xyz ordering from a coordinate system
    assert_array_equal(xyz_order(VARS['r_cs_r3']), [0,1,2])
    assert_array_equal(xyz_order(VARS['r_cs_r4']), [0,1,2,3])
    r_cs = CS(('mni-x=L->R', 'mni-y=P->A', 'mni-q'), 'mni')
    assert_raises(AxesError, xyz_order, r_cs)
    r_cs = CS(('t', 'mni-x=L->R', 'mni-z=I->S', 'mni-y=P->A'), 'mni')
    assert_array_equal(xyz_order(r_cs), [1, 3, 2, 0])
    # Can pass in own validator
    my_valtor = dict(ditch='x', leading='y', blind='z')
    r_cs = CS(('blind', 'leading', 'ditch'), 'fall')
    assert_raises(AxesError, xyz_order, r_cs)
    assert_array_equal(xyz_order(r_cs, my_valtor), [2,1,0])


def is_xyz_affable():
    # Whether there exists an xyz affine for this coordmap
    affine = np.diag([2,4,5,6,1])
    cmap = AffineTransform(VARS['d_cs_r4'], VARS['r_cs_r4'], affine)
    assert_true(is_xyz_affable(cmap))
    assert_true(is_xyz_affable(cmap.reordered_range([3,0,1,2])))
    assert_false(is_xyz_affable(cmap.reordered_domain([3,0,1,2])))
    # Can pass in own validator
    my_valtor = dict(blind='x', leading='y', ditch='z')
    r_cs = CS(('blind', 'leading', 'ditch'), 'fall')
    cmap = AffineTransform(VARS['d_cs_r3'],r_cs, affine)
    # No xyz affine if we don't use our custom dictionary
    assert_false(is_xyz_affable(cmap))
    # Is if we do
    assert_true(is_xyz_affable(cmap, my_valtor))
