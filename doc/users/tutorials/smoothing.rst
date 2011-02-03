An Introduction to Smoothing
============================

Smoothing is a process by which data points are averaged with their neighbours
in a series, such as a time series, or image. This (usually) has the effect of
blurring the sharp edges in the smoothed data. Smoothing is sometimes referred
to as filtering, because smoothing has the effect of suppressing high frequency
signal and enhancing low frequency signal. There are many different methods of
smoothing, but here we discuss smoothing with a Gaussian kernel. We hope we will
succeed in explaining this phrase in the explanation below.

Some example data for smoothing
-------------------------------

Here is a set of data, made out of random numbers, that we will use
as a pretend time series, or a single line of data from one plane
of an image.

.. plot::
    :context:
    :nofigs:
    :include-source:

    import numpy as np
    np.random.seed(5)

    # Create 40 numbers from a random normal distribution
    n = 40
    x = np.arange(n)
    y = np.random.normal(size=(n,))

Let's plot that:

.. plot::
    :context:
    :include-source:

    import matplotlib.pyplot as plt

    plt.bar(x, y)

The Gaussian kernel
-------------------

The 'kernel' for smoothing, defines the shape of the function that is used to
take the average of the neighbouring points. A Gaussian kernel is a kernel with
the shape of a Gaussian (normal distribution) curve. Here is a standard
Gaussian, with a mean of 0 and a sigma (=population standard deviation) of 1.


.. plot::
    :context:
    :include-source:

    # the Gaussian kernel shown

In the standard statistical way, we have defined the width of the Gaussian shape
in terms of sigma. However, when the Gaussian is used for
smoothing, it is usual to describe the width of the Gaussian with another
related measure, the Full Width at Half Maximum (FWHM).

The FWHM is the width of the kernel, at half of the maximum of the height of the
Gaussian. Thus, for the standard Gaussian above, the maximum height is ~0.4. The
width of the kernel at 0.2 (on the Y axis) is the FWHM. As x = -1.175 and 1.175
when y = 0.2, the FWHM is in fact 2.35. The FWHM is related to sigma by the
formula (python format):

::

    FWHM = sigma * sqrt(8*log(2))



Smoothing with the kernel
-------------------------

The basic process of smoothing is very simple. We proceed through
the data point by point. For each data point we generate a new
value that is some function of the original value at that point and
the surrounding data points.With Gaussian smoothing, the function
that is used is our Gaussian curve..

So, let us say that we are generating the new, smoothed value for
the 14th value in our example data set. We are using a Gaussian
with FWHM of 4 units on the x axis. To generate the Gaussian kernel
average for this 14th data point, we first move the Gaussian shape
to have its centre on 14 on the x axis. In order to make sure that
we don't do an overall scaling of the values aftern smoothing, we
then divide the values in the Gaussian curve by the total area
under the curve, so that the values add up to one (see the
`http://imaging.mrc-cbu.cam.ac.uk/scripts/smoothtalk.m <http://imaging.mrc-cbu.cam.ac.uk/scripts/smoothtalk.m>`_
file for how to do this in python):

|sm\_gauss\_14|

We take the values of our resulting function (from the y axis), at
each of the points in the data (the x axis). Thus we generate
Gaussian function values for 13 12 11 etc, and 15 16 17 etc. This
gives us a discrete Gaussian.

|sm\_gauss\_14d| In fact the Gaussian values for 12 13 14 15 and 16
are:



::

    0.1174    0.1975    0.2349    0.1975    0.1174

and the data values for the same points are:



::

    1.0645    0.3893    0.3490   -0.6566   -0.1946

We then multiply the Gaussian values by the values of our data, and
sum the results to get the new smoothed value for point 14. Thus,
the new value for point 14 is ... + 0.1174\*1.0645 + 0.1975\*0.3893
+ 0.2349\*0.3490 + 0.1975\*-0.6566 + 0.1174\*-0.1946 + ...

We then store this new smoothed value for future use, and move on,
to x = 15, and repeat the process, with the Gaussian kernel now
centred over 15. If we do this for each point, we eventually get
the smoothed version of our original data (see the
`http://imaging.mrc-cbu.cam.ac.uk/scripts/smoothtalk.m <http://imaging.mrc-cbu.cam.ac.uk/scripts/smoothtalk.m>`_
file again for a simple but inefficient way of doing this):

|sm\_eg\_smoothed|



Other kernels
-------------

Of course, we could have used any shape for the kernel - such as a
square wave: |sm\_sqwave| This would have the effect of replacing
each data point with a straight average of itself and the
nieghbouring points.



Smoothing in 2D
---------------

Smoothing in two dimensions follows simply from smoothing in one
dimension. This time the Gaussian kernel is not a curve, but a
cone. Here is what such a cone looks like when placed over the
central point of a plane:

|sm\_2dcone|

and the same thing with discrete values for each pixel in the
image.

|sm\_2dbar|

We then proceed as before, multiplying the values of the kernel (as
shown in the figure above) by the data in the image, to get the
smoothed value for that point, and doing the same for every point
on the image.

The procedure is the same for 3D data, except the kernel is rather
more difficult to visualize, being something like a sphere with
edges that fade out, as the cone fades out at the edges in the 2D
case.

In fact, it turns out that we don't have to generate these 2D and
3D versions of the kernel for the computations, because we get the
same result as we do by applying the full 2 or 3D kernel, if we
simply apply a one dimensional smooth sequentially in the 2 or 3
dimenensions. Thus, for 2 dimensions, we could first smooth in the
x direction, and then smooth the x-smoothed data, in the y
direction.



Why smooth?
-----------

The primary reason for smoothing is to increase signal to noise.
Smoothing increases signal to noise by the matched filter theorem.
This theorem states that the filter that will give optimum
resolution of signal from noise is a filter that is matched to the
signal. In the case of smoothing, the filter is the Gaussian
kernel. Therefore, if we are expecting signal in our images that is
of Gaussian shape, and of FWHM of say 10mm, then this signal will
best be detected after we have smoothed our images with a 10mm FWHM
Gaussian filter.The next few images show the matched filter theorem
in action. First we can generate a simulated signal in a one
dimensional set of data, by creating a Gaussian with FWHM 8 pixels,
centred over the 14th data point:

|sm\_simsignal|

Next, we add some random noise to this signal:

|sm\_noisysig|

We then smooth with a matching 8 pixel FWHM filter:

|sm\_smnoisy|

and recover our signal well from the noisy data.

Thus, we smooth with a filter that is of matched size to the
activation we wish to detect. This is of particular relevance when
comparing activation across subjects. Here, the anatomical
variability between subjects will mean that the signal across
subjects may be expected to be rather widely distributed over the
cortical surface. In such a case it may be wiser to use a wide
smoothing to detect this signal. In contrast, for a single subject
experiment, where you want to detect (for example) a thalamic
signal, which may be in the order of a few mm across, it would be
wiser to use a very narrow smoothing, or even no smoothing.



Finding the signal for any smoothing level
------------------------------------------

Sometimes you do not know the size or the shape of the signal
change that you are expecting. In these cases, it is difficult to
choose a smoothing level, because the smoothing may reduce signal
that is not of the same size and shape as the smoothing kernel.
There are ways of detecting signal at different smoothing level,
that allow appropriate corrections for multiple corrections, and
levels of smoothing. This Worsley 1996 paper describes such an
approach:
`Worsley KJ, Marret S, Neelin P, Evans AC (1996) Searching scale space for activation in PET images. Human Brain Mapping 4:74-90 <http://www.math.mcgill.ca/%7Ekeith/scale/scale.abstract.html>`_

Another promising method is to use wavelet transforms; see:
`Federico Turkheimer's wavelet introduction <http://www.irsl.org/%7Efet/Presentations/wavestatfield/wavestatfield.html>`_

Matthew Brett (FB) 19/8/99

PrinciplesSmoothing (last edited 2006-08-11 14:07:59 by
`MatthewBrett <http://imaging.mrc-cbu.cam.ac.uk/basewiki/MatthewBrett>`_)

(c) MRC Cognition and Brain Sciences Unit 2009    

.. |Edit| image:: PrinciplesSmoothing_files/moin-edit.png
.. |View| image:: PrinciplesSmoothing_files/moin-show.png
.. |Diffs| image:: PrinciplesSmoothing_files/moin-diff.png
.. |Info| image:: PrinciplesSmoothing_files/moin-info.png
.. |Subscribe| image:: PrinciplesSmoothing_files/moin-subscribe.png
.. |Raw| image:: PrinciplesSmoothing_files/moin-raw.png
.. |Print| image:: PrinciplesSmoothing_files/moin-print.png
.. |sm\_eg\_data| image:: PrinciplesSmoothing_files/sm_eg_data.gif
.. |sm\_gauss| image:: PrinciplesSmoothing_files/sm_gauss.gif
.. |sm\_gauss\_14| image:: PrinciplesSmoothing_files/sm_gauss_14.gif
.. |sm\_gauss\_14d| image:: PrinciplesSmoothing_files/sm_gauss_14d.gif
.. |sm\_eg\_smoothed| image:: PrinciplesSmoothing_files/sm_eg_smoothed.gif
.. |sm\_sqwave| image:: PrinciplesSmoothing_files/sm_sqwave.gif
.. |sm\_2dcone| image:: PrinciplesSmoothing_files/sm_2dcone.gif
.. |sm\_2dbar| image:: PrinciplesSmoothing_files/sm_2dbar.gif
.. |sm\_simsignal| image:: PrinciplesSmoothing_files/sm_simsignal.gif
.. |sm\_noisysig| image:: PrinciplesSmoothing_files/sm_noisysig.gif
.. |sm\_smnoisy| image:: PrinciplesSmoothing_files/sm_smnoisy.gif
