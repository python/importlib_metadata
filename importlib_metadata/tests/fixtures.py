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

# A pip distinfo_pkg and importlib_metadata egginfo_pkg would go here.
"""
The following are characteristics of any package that we want 
to incorporate into distinfo_pkg:
    1. Metada directory is called "name-version.dist-info"
    2. Metada is in a file called METADATA
    3. The list of files installed is called RECORD
"""
class DistInfoPkg (SiteDir):
    metadata = """Name: distinfo-pkg
Author: Steven Ma
Version: 1.0.0
"""
    def distinfo_pkg(self):
        metadata_dir = self.site_dir / "distinfo_pkg-1.0.0.dist-info"
        metadata_dir.mkdir()
        metadata_file = metadata_dir / "METADATA"
        with metadata_file.open('w') as strm:
            strm.write(self.metadata)
        metadata_record = metadata_dir / "RECORD"
        with metadata_record.open('w') as strm:
            strm.write("mod.py\n")
        (self.site_dir / "mod.py").touch()
    def setUp(self):
        super(DistInfoPkg,self).setUp()
        self.distinfo_pkg()

"""
The following are characteristics of any package that we want 
to incorporate into egginfo_pkg:
    1. Metadata directory is called "name.egg-info"
    2. Metadata is in a file called PKG-INFO (not sure)
    3. The list of files is called SOURCES.TXT

class EggInfoPkg (SiteDir):
    metadata = Name: egginfo-pkg
Author: Steven Ma
Version: 1.0.0

    def egginfo_pkg(self):
        metadata_dir = self.site_dir.mkdir("egginfo_pkg.egg-info")
        metadata_file = metadata_dir / "PKG-INFO"
        with metadata_file.open(mode='w') as strm:
            strm.write(self.metadata)
    def setUp(self):
        super(DistInfoPkg,self).setUp()
        self.egginfo_pkg()
"""
