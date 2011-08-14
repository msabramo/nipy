""" Module for testing doctests

Copied from the bottom of numpy/testing/nosetester with thanks
"""

# Import stuff with failing doctests to check for recursion
from .anothermod import a_func, AClass


# try the #random directive on the output line
def check_random_directive():
    '''
    >>> 2+2
    <BadExample object at 0x084D05AC>  #random: may vary on your system
    '''

# check the implicit "import numpy as np"
def check_implicit_np():
    '''
    >>> np.array([1,2,3])
    array([1, 2, 3])
    '''

# there's some extraneous whitespace around the correct responses
def check_whitespace_enabled():
    '''
    # whitespace after the 3
    >>> 1+2
    3 

    # whitespace before the 7
    >>> 3+4
     7
    '''

def check_fail():
    """ Confirm that a test can fail

    >>> "This is not a pipe"
    "This _is_ a pipe"
    """

def check_skip():
    """ Check that SKIP works correctly

    >>> a = b #doctest: +SKIP
    """

def check_skip_fail():
    """ Check skipping still runs the following doctest

    >>> a = b #doctest: +SKIP
    >>> True
    False
    """

def check_ellipsis():
    """ Check that ELLIPSIS works correctly

    >>> "There's an apple in front of my head" #doctest: +ELLIPSIS
    "There's an apple ...
    """
