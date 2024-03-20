import types

from jaraco.collections import Projection


def from_test_support(*names):
    """
    Return a SimpleNamespace of names from test.support.
    """
    import test.support

    return types.SimpleNamespace(**Projection(names, vars(test.support)))


try:
    from test.support import os_helper  # type: ignore
except ImportError:
    os_helper = from_test_support('FS_NONASCII', 'skip_unless_symlink')
