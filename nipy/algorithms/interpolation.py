# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
""" Image interpolators using ndimage.
"""

import os
import tempfile

import numpy as np

from scipy import ndimage

# For recognizing types that we should use nan_to_num on
INT_TYPES = np.sctypes['int'] + np.sctypes['uint'] + [np.bool]


class ImageInterpolator(object):
    """ Interpolate Image instance at arbitrary points in world space
    
    The resampling is done with scipy.ndimage.
    """
    def __init__(self, image, order=3,
                 use_mmap=False,
                 preserve_dtype=False,
                 **interp_kws):
        """ Initialize image interpolator
        
        Parameters
        ----------
        image : Image
           Image to be interpolated.  Needs to implement 'get_data' and
           'coordmap' 
        order : int, optional
           order of spline interpolation as used in scipy.ndimage.
           Default is 3.
        use_mmap : bool, optional
           Whether to use memory mapping to create knots.  Default False
        preserve_dtype : bool, optional
           Whether to preserve the data dtype in the underlying
           resampling.  Default is False.   If True, you may lose
           precision in the resampling.
        **interp_kws :
           Keyword parameters for interpolating routine
           (ndimage.map_coordinates). Includes:
           
           * mode --  Points outside the boundaries of the input are filled
                      according to the given mode ('constant', 'nearest',
                      'reflect' or 'wrap'). Default is 'constant'.
           * cval -- fill value if mode is 'constant'
           Keywords for ndimage.map_coordinates interpolation
        """
        self.image = image
        self.order = order
        self._datafile = None
        self.preserve_dtype = preserve_dtype
        self.interp_kws = interp_kws
        self._buildknots(use_mmap)

    def _buildknots(self, use_mmap):
        preserve_dtype = self.preserve_dtype
        data = self.image.get_data()
        if data.dtype.type not in INT_TYPES:
            data = np.nan_to_num(data)
        if self.order > 1:
            if preserve_dtype:
                out_dtype = data.dtype
            else:
                out_dtype = np.float
            data = ndimage.spline_filter(
                data,
                order=self.order,
                output=out_dtype)
        elif not preserve_dtype:
            data = data.astype(np.float64)
        if not use_mmap:
            self.data = data
            return
        if self._datafile is None:
            _, fname = tempfile.mkstemp()
            self._datafile = open(fname, mode='wb')
        else:
            self._datafile = open(self._datafile.name, 'wb')
        data.tofile(self._datafile)
        datashape = data.shape
        dtype = data.dtype
        del(data)
        self._datafile.close()
        self._datafile = open(self._datafile.name)
        self.data = np.memmap(self._datafile.name, dtype=dtype,
                              mode='r+', shape=datashape)

    def __del__(self):
        if self._datafile:
            self._datafile.close()
            try:
                os.remove(self._datafile.name)
            except:
                pass

    def evaluate(self, points, **interp_kws):
        """ Resample image at points in world space
        
        Parameters
        ----------
        points : array
           values in self.image.coordmap.output_coords.  Each row is a
	   point. 
        **interp_kws : dict
           Keyword parameters for interpolating routine
           (ndimage.map_coordinates). Includes:
           
           * mode --  Points outside the boundaries of the input are filled
                      according to the given mode ('constant', 'nearest',
                      'reflect' or 'wrap'). Default is 'constant'.
           * cval -- fill value if mode is 'constant'

           These are merged with any interp_kws stored as
           ``self.interp_kws`` before passing into interpolation function.

        Returns
        -------
        V : ndarray
           interpolator of self.image evaluated at points
        """
        interp_dict = self.interp_kws.copy()
        interp_dict.update(interp_kws)
        points = np.array(points, np.float64)
        output_shape = points.shape[1:]
        points.shape = (points.shape[0], np.product(output_shape))
        cmapi = self.image.coordmap.inverse()
        voxels = cmapi(points.T).T
        if self.preserve_dtype:
            out_dtype = self.data.dtype
        else:
            out_dtype = np.float
        V = ndimage.map_coordinates(self.data, 
                                    voxels,
                                    order=self.order,
                                    prefilter=False,
                                    output=out_dtype,
                                    **interp_dict)
        # ndimage.map_coordinates returns a flat array,
        # it needs to be reshaped to the original shape
        V.shape = output_shape
        return V
