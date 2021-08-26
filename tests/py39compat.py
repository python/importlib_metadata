try:
    from test.support.os_helper import FS_NONASCII as FS_NONASCII
except ImportError:
    from test.support import FS_NONASCII as FS_NONASCII  # noqa
