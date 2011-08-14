""" Don't check this module, it's for checking recursion """

import nose.plugins

def setup_module():
    raise nose.plugins.skip.SkipTest('This is not for testing')


def a_func():
    """
    >>> True
    False
    """
    pass


class AClass(object):
    def __init__(self):
        """ A broken doctest

        >>> 1
        2
        """
        pass

    def a_method(self):
        """ Another one

        >>> 'Hi'
        'There'
        """
        pass

