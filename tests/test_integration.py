import sys
import pathlib
import unittest
import packaging.requirements
import packaging.version

from . import fixtures
from importlib_metadata import (
    MetadataPathFinder,
    _compat,
    distribution,
    distributions,
    entry_points,
    metadata,
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
        class ModuleFreeFinder(fixtures.NullFinder):
            """
            A finder without an __module__ attribute
            """

            def __getattribute__(self, name):
                if name == '__module__':
                    raise AttributeError(name)
                return super().__getattribute__(name)

        self.fixtures.enter_context(fixtures.install_finder(ModuleFreeFinder()))
        _compat.disable_stdlib_finder()


class OldStdlibFinderTests(fixtures.DistInfoPkgOffPath, unittest.TestCase):
    def setUp(self):
        python_version = sys.version_info[:2]
        if python_version < (3, 8) or python_version > (3, 9):
            self.skipTest("Tests specific for Python 3.8/3.9")
        super().setUp()

    def _meta_path_finder(self):
        from importlib.metadata import DistributionFinder, PathDistribution
        from importlib.util import spec_from_file_location

        path = pathlib.Path(self.site_dir)

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
        assert version("distinfo_pkg") > "0"
        assert list(metadata("distinfo_pkg"))
        assert list(entry_points(group="entries"))


class DistSearch(unittest.TestCase):
    def test_search_dist_dirs(self):
        """
        Pip needs the _search_paths interface to locate
        distribution metadata dirs. Protect it for PyPA
        use-cases (only). Ref python/importlib_metadata#111.
        """
        res = MetadataPathFinder._search_paths('any-name', [])
        assert list(res) == []

    def test_interleaved_discovery(self):
        """
        When the search is cached, it is
        possible for searches to be interleaved, so make sure
        those use-cases are safe.

        Ref #293
        """
        dists = distributions()
        next(dists)
        version('importlib_metadata')
        next(dists)
