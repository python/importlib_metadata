import sys
import shutil
import tempfile
import contextlib

try:
    from contextlib import ExitStack
except ImportError:
    from contextlib2 import ExitStack

try:
    import pathlib
except ImportError:
    import pathlib2 as pathlib


__metaclass__ = type


class SiteDir:
    @staticmethod
    @contextlib.contextmanager
    def site_dir():
        tmpdir = tempfile.mkdtemp()
        sys.path[:0] = [tmpdir]
        try:
            yield pathlib.Path(tmpdir)
        finally:
            sys.path.remove(tmpdir)
            shutil.rmtree(tmpdir)

    def setUp(self):
        self.fixtures = ExitStack()
        self.addCleanup(self.fixtures.close)
        self.site_dir = self.fixtures.enter_context(self.site_dir())
