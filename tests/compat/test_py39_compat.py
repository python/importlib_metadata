import sys
import pathlib
import unittest

from .. import fixtures
from importlib_metadata import (
    distribution,
    distributions,
    entry_points,
    metadata,
    version,
)


class OldStdlibFinderTests(fixtures.DistInfoPkgOffPath, unittest.TestCase):
    def setUp(self):
        if sys.version_info >= (3, 10):
            self.skipTest("Tests specific for Python 3.8/3.9")
        super().setUp()

    def _meta_path_finder(self):
        from importlib.metadata import (
            Distribution,
            DistributionFinder,
            PathDistribution,
        )
        from importlib.util import spec_from_file_location

        path = pathlib.Path(self.site_dir)

        class CustomDistribution(Distribution):
            def __init__(self, name, path):
                self.name = name
                self._path_distribution = PathDistribution(path)

            def read_text(self, filename):
                return self._path_distribution.read_text(filename)

            def locate_file(self, path):
                return self._path_distribution.locate_file(path)

        class CustomFinder:
            @classmethod
            def find_spec(cls, fullname, _path=None, _target=None):
                candidate = pathlib.Path(path, *fullname.split(".")).with_suffix(".py")
                if candidate.exists():
                    return spec_from_file_location(fullname, candidate)

            @classmethod
            def find_distributions(self, context=DistributionFinder.Context()):
                for dist_info in path.glob("*.dist-info"):
                    yield PathDistribution(dist_info)
                    name, _, _ = str(dist_info).partition("-")
                    yield CustomDistribution(name + "_custom", dist_info)

        return CustomFinder

    def test_compatibility_with_old_stdlib_path_distribution(self):
        """
        Given a custom finder that uses Python 3.8/3.9 importlib.metadata is installed,
        when importlib_metadata functions are called, there should be no exceptions.
        Ref python/importlib_metadata#396.
        """
        self.fixtures.enter_context(fixtures.install_finder(self._meta_path_finder()))

        assert list(distributions())
        assert distribution("distinfo_pkg")
        assert distribution("distinfo_pkg_custom")
        assert version("distinfo_pkg") > "0"
        assert version("distinfo_pkg_custom") > "0"
        assert list(metadata("distinfo_pkg"))
        assert list(metadata("distinfo_pkg_custom"))
        assert list(entry_points(group="entries"))
