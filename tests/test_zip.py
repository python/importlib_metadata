import sys
import unittest

from . import fixtures
from .fixtures import not_none
from importlib_metadata import (
    PackageNotFoundError,
    distribution,
    distributions,
    entry_points,
    files,
    version,
)


class TestZip(fixtures.ZipFixtures, unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        self._fixture_on_path('example-21.12-py3-none-any.whl')

    def test_zip_version(self) -> None:
        self.assertEqual(version('example'), '21.12')

    def test_zip_version_does_not_match(self) -> None:
        with self.assertRaises(PackageNotFoundError):
            version('definitely-not-installed')

    def test_zip_entry_points(self) -> None:
        scripts = entry_points(group='console_scripts')
        entry_point = scripts['example']
        self.assertEqual(entry_point.value, 'example:main')
        entry_point = scripts['Example']
        self.assertEqual(entry_point.value, 'example:main')

    def test_missing_metadata(self) -> None:
        self.assertIsNone(distribution('example').read_text('does not exist'))

    def test_case_insensitive(self) -> None:
        self.assertEqual(version('Example'), '21.12')

    def test_files(self) -> None:
        for file in not_none(files('example')):
            path = str(file.dist.locate_file(file))
            assert '.whl/' in path, path

    def test_one_distribution(self) -> None:
        dists = list(distributions(path=sys.path[:1]))
        assert len(dists) == 1


class TestEgg(TestZip):
    def setUp(self) -> None:
        super().setUp()
        self._fixture_on_path('example-21.12-py3.6.egg')

    def test_files(self) -> None:
        for file in not_none(files('example')):
            path = str(file.dist.locate_file(file))
            assert '.egg/' in path, path

    def test_normalized_name(self) -> None:
        dist = distribution('example')
        assert dist._normalized_name == 'example'
