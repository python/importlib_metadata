"""
The published protocols must also describe the objects supplied by
``importlib.metadata`` in the running Python (#486).
"""

import importlib.metadata as stdlib
import pathlib
import sys
import tempfile
import unittest

from importlib_metadata import IDistribution, IPackagePath, PackageMetadata
from importlib_metadata.compat import py312


class StdlibProtocolTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmpdir.cleanup)
        tmp_path = pathlib.Path(self.tmpdir.name)
        dist_info = tmp_path / 'protocol_sample-1.0.dist-info'
        dist_info.mkdir()
        (dist_info / 'METADATA').write_text(
            'Name: protocol-sample\nVersion: 1.0\n', encoding='utf-8'
        )
        self.dist = stdlib.PathDistribution(dist_info)

    def test_stdlib_distribution_conforms(self):
        assert py312.conforms(self.dist, IDistribution)

    @unittest.skipIf(
        sys.version_info < (3, 13), "stdlib Distribution.origin added in Python 3.13"
    )
    def test_stdlib_distribution_matches_protocol(self):
        assert isinstance(self.dist, IDistribution)

    def test_stdlib_metadata_matches_protocol(self):
        assert isinstance(self.dist.metadata, PackageMetadata)

    def test_stdlib_package_path_matches_protocol(self):
        package_path = stdlib.PackagePath('protocol_sample/__init__.py')
        package_path.hash = None
        package_path.size = 0
        package_path.dist = self.dist
        assert isinstance(package_path, IPackagePath)
