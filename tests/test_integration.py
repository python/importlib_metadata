"""
Test behaviors specific to importlib_metadata.

These tests are excluded downstream in CPython as they
test functionality only in importlib_metadata or require
behaviors ('packaging') that aren't available in the
stdlib.
"""

import unittest
import packaging.requirements
import packaging.version

from . import fixtures
from importlib_metadata import (
    _compat,
    version,
)


class IntegrationTests(fixtures.DistInfoPkg, unittest.TestCase):
    def test_package_spec_installed(self):
        """
        Illustrate the recommended procedure to determine if
        a specified version of a package is installed.
        """

        def is_installed(package_spec):
            req = packaging.requirements.Requirement(package_spec)
            return version(req.name) in req.specifier

        assert is_installed('distinfo-pkg==1.0')
        assert is_installed('distinfo-pkg>=1.0,<2.0')
        assert not is_installed('distinfo-pkg<1.0')


class FinderTests(fixtures.Fixtures, unittest.TestCase):
    def test_finder_without_module(self):
        class ModuleFreeFinder:
            """
            A finder without an __module__ attribute
            """

            def find_module(self, name):
                pass

            def __getattribute__(self, name):
                if name == '__module__':
                    raise AttributeError(name)
                return super().__getattribute__(name)

        self.fixtures.enter_context(fixtures.install_finder(ModuleFreeFinder()))
        _compat.disable_stdlib_finder()
