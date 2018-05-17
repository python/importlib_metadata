import unittest
import re
import importlib

import importlib_metadata


class BasicTests(unittest.TestCase):
    version_pattern = r'\d+\.\d+(\.\d)?'

    def test_retrieves_version_of_self(self):
        dist = importlib_metadata.Distribution.for_module(importlib_metadata)
        assert isinstance(dist.version, str)
        assert re.match(self.version_pattern, dist.version)

    def test_retrieves_version_of_pip(self):
        """
        Assume pip is installed and retrieve the version of pip.
        """
        pip = importlib.import_module('pip')
        dist = importlib_metadata.Distribution.for_module(pip)
        assert isinstance(dist.version, str)
        assert re.match(self.version_pattern, dist.version)

    def test_for_name_does_not_exist(self):
        with self.assertRaises(importlib_metadata.PackageNotFound):
            importlib_metadata.Distribution.for_name('does-not-exist')
