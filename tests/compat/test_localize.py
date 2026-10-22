"""
Tests for the adaptation of objects supplied by ``importlib.metadata``
providers into their ``importlib_metadata`` counterparts (#486).
"""

import importlib.metadata as stdlib
import pathlib
import unittest
import warnings

import importlib_metadata
import importlib_metadata._adapters
from importlib_metadata import distribution, distributions, entry_points, files
from importlib_metadata._compat import localize

from .. import fixtures


class StdlibProviderTests(fixtures.DistInfoPkgOffPath, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.fixtures.enter_context(fixtures.install_finder(self._finder()))

    def _finder(self):
        """
        A finder supplying distributions from the stdlib, as a third party
        provider built on importlib.metadata would.
        """
        site_dir = pathlib.Path(self.site_dir)

        class StdlibFinder:
            @staticmethod
            def find_spec(*args, **kwargs):
                return None

            @staticmethod
            def find_distributions(context=None):
                return map(stdlib.PathDistribution, site_dir.glob('*.dist-info'))

        return StdlibFinder()

    def test_from_name_localized(self):
        assert isinstance(distribution('distinfo-pkg'), importlib_metadata.Distribution)

    def test_discover_localized(self):
        assert all(
            isinstance(dist, importlib_metadata.Distribution)
            for dist in distributions()
        )

    def test_metadata_localized(self):
        meta = distribution('distinfo-pkg').metadata
        assert isinstance(meta, importlib_metadata._adapters.Message)
        assert meta.json['name'] == 'distinfo-pkg'

    def test_files_localized(self):
        assert all(
            isinstance(file, importlib_metadata.PackagePath)
            for file in files('distinfo-pkg')
        )

    def test_entry_points_selectable(self):
        """
        Entry points are selectable, even though the provider knows
        nothing of EntryPoints.
        """
        assert entry_points(group='entries')['main'].value == 'mod:main'


class CustomProviderTests(fixtures.DistInfoPkgOffPath, unittest.TestCase):
    """
    A provider deriving its own class from importlib.metadata, as the
    custom provider example in the CPython docs does.
    """

    def setUp(self):
        super().setUp()
        self.fixtures.enter_context(fixtures.install_finder(self._finder()))

    def _finder(self):
        site_dir = pathlib.Path(self.site_dir)

        class CustomDistribution(stdlib.Distribution):
            def __init__(self, path):
                self._delegate = stdlib.PathDistribution(path)

            def read_text(self, filename):
                return self._delegate.read_text(filename)

            def locate_file(self, path):
                return self._delegate.locate_file(path)

        class CustomFinder:
            @staticmethod
            def find_spec(*args, **kwargs):
                return None

            @staticmethod
            def find_distributions(context=None):
                return map(CustomDistribution, site_dir.glob('*.dist-info'))

        return CustomFinder()

    def test_conforming_provider_is_not_warned_about(self):
        """
        Implementing the interface is enough; deriving from this package
        is not required (#486).
        """
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter('always')
            assert distribution('distinfo-pkg').version == '1.0.0'
        assert not [str(warning.message) for warning in caught]


class ConformanceCheckTests(unittest.TestCase):
    def test_properties_are_not_evaluated(self):
        """
        Deciding conformance consults the class, never the instance.

        Through Python 3.11, isinstance() against a runtime-checkable
        protocol evaluates property members, so a property that raises
        would escape from an ordinary distribution lookup.
        See python/cpython#102433.
        """

        class Hostile(stdlib.Distribution):
            def read_text(self, filename):
                return None

            def locate_file(self, path):
                return None

            @property
            def metadata(self):
                raise RuntimeError("must not be evaluated")

        hostile = Hostile()
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter('always')
            assert localize.dist(hostile) is hostile
        assert not [str(warning.message) for warning in caught]
