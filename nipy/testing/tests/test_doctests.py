# test doctest machinery

import sys
from StringIO import StringIO

from nose.tools import assert_true, assert_equal

from . import apkg

def test_doctests():
    sys_out = sys.stdout
    sys_err = sys.stderr
    try: # test output designed to fail looks rather frightening
        sys.stdout = StringIO()
        sys.stderr = StringIO()
        res = apkg.test(verbose=3, extra_argv=['--doctest-tests',
                                               '--nologcapture',
                                               '--nocapture'])
    finally:
        sys.stdout = sys_out
        sys.stderr = sys_err
    assert_equal(len(res.errors), 0)
    failure_names = [t.id().split('.')[-1] for t, msg in res.failures]
    assert_equal(set(failure_names), set(['check_fail',
                                          'check_skip_fail']))

