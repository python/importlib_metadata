try:
    from test.support.os_helper import FS_NONASCII
except ImportError:
    from test.support import FS_NONASCII  # noqa


try:
    from test.support.import_helper import import_module
except ImportError:
    from test.support import import_module  # noqa
