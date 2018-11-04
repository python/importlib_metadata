from __future__ import unicode_literals

import re
import unittest
import importlib
import importlib_metadata
import sys
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

from importlib_metadata import _hooks


class BasicTests(unittest.TestCase):
    version_pattern = r'\d+\.\d+(\.\d)?'

    def test_retrieves_version_of_pip(self):
        # Assume pip is installed and retrieve the version of pip.
        dist = importlib_metadata.Distribution.from_name('pip')
        assert isinstance(dist.version, str)
        assert re.match(self.version_pattern, dist.version)

    def test_for_name_does_not_exist(self):
        with self.assertRaises(importlib_metadata.PackageNotFoundError):
            importlib_metadata.Distribution.from_name('does-not-exist')

    def test_new_style_classes(self):
        self.assertIsInstance(importlib_metadata.Distribution, type)
        self.assertIsInstance(_hooks.MetadataPathFinder, type)
        self.assertIsInstance(_hooks.WheelMetadataFinder, type)
        self.assertIsInstance(_hooks.WheelDistribution, type)


class ImportTests(unittest.TestCase):
    def test_import_nonexistent_module(self):
        # Ensure that the MetadataPathFinder does not crash an import of a
        # non-existant module.
        with self.assertRaises(ImportError):
            importlib.import_module('does_not_exist')

    def test_resolve(self):
        entry_points = importlib_metadata.entry_points('pip')
        main = importlib_metadata.resolve(
            entry_points.get('console_scripts', 'pip'))
        import pip._internal
        self.assertEqual(main, pip._internal.main)

    def test_resolve_invalid(self):
        self.assertRaises(ValueError, importlib_metadata.resolve, 'bogus.ep')


class NameNormalizationTests(unittest.TestCase):
    @staticmethod
    def pkg_with_dashes(site_dir):
        metadata_dir = site_dir / 'my_pkg.dist-info'
        metadata_dir.mkdir()
        metadata = metadata_dir / 'METADATA'
        with metadata.open('w') as strm:
            strm.write('Version: 1.0\n')
        return 'my-pkg'

    @staticmethod
    @contextlib.contextmanager
    def site_dir():
        tmpdir = tempfile.mkdtemp()
        sys.path[:0] = [tmpdir]
        try:
            yield pathlib.Path(tmpdir)
        finally:
            sys.path.remove(tmpdir)

    def setUp(self):
        self.fixtures = ExitStack()
        self.site_dir = self.fixtures.enter_context(self.site_dir())

    def tearDown(self):
        self.fixtures.close()

    def test_dashes_in_dist_name_found_as_underscores(self):
        """
        For a package with a dash in the name, the dist-info metadata
        uses underscores in the name. Ensure the metadata loads.
        """
        pkg_name = self.pkg_with_dashes(self.site_dir)
        assert importlib_metadata.version(pkg_name) == '1.0'
