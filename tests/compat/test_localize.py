"""
Tests for the adaptation of objects supplied by ``importlib.metadata``
providers into their ``importlib_metadata`` counterparts (#486).
"""

import importlib.metadata as stdlib
import pathlib
import unittest

import importlib_metadata
import importlib_metadata._adapters
from importlib_metadata import distribution, distributions, entry_points, files

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
