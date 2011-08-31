""" Utilities for working with recarrays

Most of these utilities are copied from matplotlib.cbook or matplotlib.mlab with
thanks.

There follows the matplotlib license:

LICENSE AGREEMENT FOR MATPLOTLIB 1.1.0
--------------------------------------

1. This LICENSE AGREEMENT is between John D. Hunter ("JDH"), and the
Individual or Organization ("Licensee") accessing and otherwise using
matplotlib software in source or binary form and its associated
documentation.

2. Subject to the terms and conditions of this License Agreement, JDH
hereby grants Licensee a nonexclusive, royalty-free, world-wide license
to reproduce, analyze, test, perform and/or display publicly, prepare
derivative works, distribute, and otherwise use matplotlib 1.1.0
alone or in any derivative version, provided, however, that JDH's
License Agreement and JDH's notice of copyright, i.e., "Copyright (c)
2002-2011 John D. Hunter; All Rights Reserved" are retained in
matplotlib 1.1.0 alone or in any derivative version prepared by
Licensee.

3. In the event Licensee prepares a derivative work that is based on or
incorporates matplotlib 1.1.0 or any part thereof, and wants to
make the derivative work available to others as provided herein, then
Licensee hereby agrees to include in any such work a brief summary of
the changes made to matplotlib 1.1.0.

4. JDH is making matplotlib 1.1.0 available to Licensee on an "AS
IS" basis.  JDH MAKES NO REPRESENTATIONS OR WARRANTIES, EXPRESS OR
IMPLIED.  BY WAY OF EXAMPLE, BUT NOT LIMITATION, JDH MAKES NO AND
DISCLAIMS ANY REPRESENTATION OR WARRANTY OF MERCHANTABILITY OR FITNESS
FOR ANY PARTICULAR PURPOSE OR THAT THE USE OF MATPLOTLIB 1.1.0
WILL NOT INFRINGE ANY THIRD PARTY RIGHTS.

5. JDH SHALL NOT BE LIABLE TO LICENSEE OR ANY OTHER USERS OF MATPLOTLIB
1.1.0 FOR ANY INCIDENTAL, SPECIAL, OR CONSEQUENTIAL DAMAGES OR
LOSS AS A RESULT OF MODIFYING, DISTRIBUTING, OR OTHERWISE USING
MATPLOTLIB 1.1.0, OR ANY DERIVATIVE THEREOF, EVEN IF ADVISED OF
THE POSSIBILITY THEREOF.

6. This License Agreement will automatically terminate upon a material
breach of its terms and conditions.

7. Nothing in this License Agreement shall be deemed to create any
relationship of agency, partnership, or joint venture between JDH and
Licensee.  This License Agreement does not grant permission to use JDH
trademarks or trade name in a trademark sense to endorse or promote
products or services of Licensee, or any third party.

8. By copying, installing or otherwise using matplotlib 1.1.0,
Licensee agrees to be bound by the terms and conditions of this License
Agreement.
"""
import numpy as np
from numpy import ma

# From matplotlib.cbook
def iterable(obj):
    'return true if *obj* is iterable'
    try:
        iter(obj)
    except TypeError:
        return False
    return True


# From matplotlib.cbook
def is_string_like(obj):
    'Return True if *obj* looks like a string'
    if isinstance(obj, (str, unicode)): return True
    # numpy strings are subclass of str, ma strings are not
    if ma.isMaskedArray(obj):
        if obj.ndim == 0 and obj.dtype.kind in 'SU':
            return True
        else:
            return False
    try: obj + ''
    except: return False
    return True


# From matplotlib.mlab
def rec_append_fields(rec, names, arrs, dtypes=None):
    """
    Return a new record array with field names populated with data
    from arrays in *arrs*.  If appending a single field, then *names*,
    *arrs* and *dtypes* do not have to be lists. They can just be the
    values themselves.
    """
    if (not is_string_like(names) and iterable(names) \
            and len(names) and is_string_like(names[0])):
        if len(names) != len(arrs):
            raise ValueError, "number of arrays do not match number of names"
    else: # we have only 1 name and 1 array
        names = [names]
        arrs = [arrs]
    arrs = map(np.asarray, arrs)
    if dtypes is None:
        dtypes = [a.dtype for a in arrs]
    elif not iterable(dtypes):
        dtypes = [dtypes]
    if len(arrs) != len(dtypes):
        if len(dtypes) == 1:
            dtypes = dtypes * len(arrs)
        else:
            raise ValueError("dtypes must be None, a single dtype or a list")

    newdtype = np.dtype(rec.dtype.descr + zip(names, dtypes))
    newrec = np.recarray(rec.shape, dtype=newdtype)
    for field in rec.dtype.fields:
        newrec[field] = rec[field]
    for name, arr in zip(names, arrs):
        newrec[name] = arr
    return newrec


# From matplotlib.mlab
def rec_drop_fields(rec, names):
    """
    Return a new numpy record array with fields in *names* dropped.
    """
    names = set(names)
    newdtype = np.dtype([(name, rec.dtype[name]) for name in rec.dtype.names
                       if name not in names])
    newrec = np.recarray(rec.shape, dtype=newdtype)
    for field in newdtype.names:
        newrec[field] = rec[field]
    return newrec


def rec_keep_fields(rec, names):
    """
    Return a new numpy record array with only fields listed in names
    """
    if is_string_like(names):
        names = names.split(',')
    arrays = []
    for name in names:
        arrays.append(rec[name])
    return np.rec.fromarrays(arrays, names=names)

