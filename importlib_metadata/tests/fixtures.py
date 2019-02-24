import sys
import os
import shutil
import tempfile
import contextlib
import textwrap

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
Requires-Dist: wheel >= 1.0
Requires-Dist: pytest; extra == 'test'
"""
    def distinfo_pkg(self):
        build_files({
            "distinfo_pkg-1.0.0.dist-info": {
                "METADATA": self.metadata,
                "RECORD": "mod.py,sha256=abc,20\n",
                "entry_points.txt" : """
                    [entries]
                    main = mod:main
                """
            },
            "mod.py": """
                def main():
                    print("hello world")
                """,
        },prefix=str(self.site_dir))
    def setUp(self):
        super(DistInfoPkg,self).setUp()
        self.distinfo_pkg()

"""
The following are characteristics of any package that we want 
to incorporate into egginfo_pkg:
    1. Metadata directory is called "name.egg-info"
    2. Metadata is in a file called PKG-INFO (not sure)
    3. The list of files is called SOURCES.txt
"""

class EggInfoPkg (SiteDir):
    eggmetadata = """Name: egginfo-pkg
Author: Steven Ma
License: Unknown
Version: 1.0.0
Classifier: Intended Audience :: Developers
Classifier: Topic :: Software Development :: Libraries"""

    def egginfo_pkg(self):
        build_files({
            "egginfo_pkg.egg-info": {
                "PKG-INFO": self.eggmetadata,
                "SOURCES.txt": """
                    mod.py
                    egginfo_pkg.egg-info/top_level.txt
                """,
                "entry_points.txt" : """
                    [entries]
                    main = mod:main
                """,
                "requires.txt": """
                    wheel >= 1.0; python_version >= "2.7"
                    [test]
                    pytest
                """,
                "top_level.txt": "mod\n"
            },
            "mod.py": """
                def main():
                    print("hello world")
                """,
        },prefix=str(self.site_dir))
    def setUp(self):
        super(EggInfoPkg,self).setUp()
        self.egginfo_pkg()

def build_files(file_defs, prefix=""):
    """
    Build a set of files/directories, as described by the
    file_defs dictionary.
    Each key/value pair in the dictionary is interpreted as
    a filename/contents
    pair. If the contents value is a dictionary, a directory
    is created, and the
    dictionary interpreted as the files within it, recursively.
    For example:
    {"README.txt": "A README file",
     "foo": {
        "__init__.py": "",
        "bar": {
            "__init__.py": "",
        },
        "baz.py": "# Some code",
     }
    }
    """
    for name, contents in file_defs.items():
        full_name = os.path.join(prefix, name)
        if isinstance(contents, dict):
            # Keep makedirs for now. Pathlib later.
            os.makedirs(full_name)
            build_files(contents, prefix=full_name)
        else:
            if isinstance(contents, bytes):
                with open(full_name, 'wb') as f:
                    f.write(contents)
            else:
                with open(full_name, 'w') as f:
                    f.write(DALS(contents))

# Unindents the above triple quote text for formatting
def DALS(str):
    return textwrap.dedent(str).lstrip()