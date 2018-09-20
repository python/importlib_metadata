import sys
import unittest
import importlib_metadata

from types import ModuleType

try:
    from contextlib import ExitStack
except ImportError:
    from contextlib2 import ExitStack

from importlib_resources import path


class BespokeLoader:
    archive = 'bespoke'


class TestZip(unittest.TestCase):
    def setUp(self):
        # Find the path to the example.*.whl so we can add it to the front of
        # sys.path, where we'll then try to find the metadata thereof.
        self.resources = ExitStack()
        self.addCleanup(self.resources.close)
        wheel = self.resources.enter_context(
            path('importlib_metadata.tests.data',
                 'example-21.12-py3-none-any.whl'))
        sys.path.insert(0, str(wheel))
        self.resources.callback(sys.path.pop, 0)

    def test_zip_version(self):
        self.assertEqual(importlib_metadata.version('example'), '21.12')

    def test_zip_entry_points(self):
        parser = importlib_metadata.entry_points('example')
        entry_point = parser.get('console_scripts', 'example')
        self.assertEqual(entry_point, 'example:main')

    def test_not_a_zip(self):
        # For coverage purposes, this module is importable, but has neither a
        # location on the file system, nor a .archive attribute.
        sys.modules['bespoke'] = ModuleType('bespoke')
        self.resources.callback(sys.modules.pop, 'bespoke')
        self.assertRaises(ImportError,
                          importlib_metadata.version,
                          'bespoke')

    def test_unversioned_dist_info(self):
        # For coverage purposes, give the module an unversioned .archive
        # attribute.
        bespoke = sys.modules['bespoke'] = ModuleType('bespoke')
        bespoke.__loader__ = BespokeLoader()
        self.resources.callback(sys.modules.pop, 'bespoke')
        self.assertRaises(ImportError,
                          importlib_metadata.version,
                          'bespoke')

    def test_missing_metadata(self):
        distribution = importlib_metadata.distribution('example')
        self.assertIsNone(distribution.read_text('does not exist'))
