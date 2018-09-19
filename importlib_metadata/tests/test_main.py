import re
import unittest
import importlib
import importlib_metadata

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
