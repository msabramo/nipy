# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
import os
import warnings
from shutil import rmtree
from tempfile import mkstemp, mkdtemp

import numpy as np
from nipy.testing import TestCase, funcfile, dec

from nipy.io.api import load_image

import nipy.modalities.fmri.fmristat.model as model
from nipy.modalities.fmri.api import FmriImageList

from nipy.modalities.fmri.formula import T, Formula

# FIXME: these things are obsolete
# from nipy.fixes.scipy.stats.models.contrast import Contrast

def setup():
    # Suppress warnings during tests to reduce noise
    warnings.simplefilter("ignore")

def teardown():
    # Clear list of warning filters
    warnings.resetwarnings()


class test_fMRIstat_model(TestCase):

    def setUp(self):
        # Using mkstemp instead of NamedTemporaryFile.  MS Windows
        # cannot reopen files created with NamedTemporaryFile.
        _, self.ar1 = mkstemp(prefix='ar1_', suffix='.nii')
        _, self.resid_OLS = mkstemp(prefix='resid_OSL_', suffix='.nii')
        _, self.F = mkstemp(prefix='F_', suffix='.nii')
        _, self.resid = mkstemp(prefix='resid_', suffix='.nii')
        # Use a temp directory for the model.output_T images
        self.out_dir = mkdtemp()

    def tearDown(self):
        os.remove(self.ar1)
        os.remove(self.resid_OLS)
        os.remove(self.F)
        os.remove(self.resid)
        rmtree(self.out_dir)

    # FIXME: This does many things, but it does not test any values
    # with asserts.
    def testrun(self):
        funcim = load_image(funcfile)
        fmriims = FmriImageList.from_image(funcim, volume_start_times=2.)

        f1 = T
        f2 = T**2
        f3 = T**3

        f = Formula([f1,f2,f3])
        times = fmriims.volume_start_times.view(np.dtype([('t', np.float)]))
        design, contrasts = f.design(times, contrasts={'var1':Formula([f1]),
                                                       'var2':Formula([f1,f2])})

#         c = Contrast(f1, f)
#         c.compute_matrix(fmriims.volume_start_times)
#         c2 = Contrast(f1 + f2, f)
#         c2.compute_matrix(fmriims.volume_start_times)

        outputs = []
        outputs.append(model.output_AR1(self.ar1, fmriims, clobber=True))
        outputs.append(model.output_resid(self.resid_OLS, fmriims, 
                                          clobber=True))
        ols = model.OLSModel(fmriims, f, outputs)
        ols.execute()

        outputs = []
        out_fn = os.path.join(self.out_dir, 'out.nii')
        outputs.append(model.output_T(out_fn, contrasts['var1'], fmriims, clobber=True))
        outputs.append(model.output_F(self.F, contrasts['var2'], fmriims, clobber=True))
        outputs.append(model.output_resid(self.resid, fmriims, clobber=True))
        rho = load_image(self.ar1)
        ar = model.AR1Model(fmriims, f, rho, outputs)
        ar.execute()
