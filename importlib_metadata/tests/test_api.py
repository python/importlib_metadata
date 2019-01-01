import re
import textwrap
import unittest
import importlib_metadata
import packaging.requirements

try:
    from collections.abc import Iterator
except ImportError:
    from collections import Iterator  # noqa: F401

try:
    from builtins import str as text
except ImportError:
    from __builtin__ import unicode as text


class APITests(unittest.TestCase):
    version_pattern = r'\d+\.\d+(\.\d)?'

    def test_retrieves_version_of_self(self):
        version = importlib_metadata.version('importlib_metadata')
        assert isinstance(version, text)
        assert re.match(self.version_pattern, version)

    def test_retrieves_version_of_pip(self):
        # Assume pip is installed and retrieve the version of pip.
        version = importlib_metadata.version('pip')
        assert isinstance(version, text)
        assert re.match(self.version_pattern, version)

    def test_for_name_does_not_exist(self):
        with self.assertRaises(importlib_metadata.PackageNotFoundError):
            importlib_metadata.distribution('does-not-exist')

    def test_for_top_level(self):
        distribution = importlib_metadata.distribution('importlib_metadata')
        self.assertEqual(
            distribution.read_text('top_level.txt').strip(),
            'importlib_metadata')

    def test_read_text(self):
        top_level = [
            path for path in importlib_metadata.files('importlib_metadata')
            if path.name == 'top_level.txt'
            ][0]
        self.assertEqual(top_level.read_text(), 'importlib_metadata\n')

    def test_entry_points(self):
        scripts = importlib_metadata.entry_points()['console_scripts']
        scripts = dict(scripts)
        pip_ep = scripts['pip']
        # We should probably not be dependent on a third party package's
        # internal API staying stable.
        self.assertEqual(pip_ep.value, 'pip._internal:main')
        self.assertEqual(pip_ep.extras, [])

    def test_metadata_for_this_package(self):
        md = importlib_metadata.metadata('importlib_metadata')
        assert md['author'] == 'Barry Warsaw'
        assert md['LICENSE'] == 'Apache Software License'
        assert md['Name'] == 'importlib-metadata'
        classifiers = md.get_all('Classifier')
        assert 'Topic :: Software Development :: Libraries' in classifiers

    def test_importlib_metadata_version(self):
        assert re.match(self.version_pattern, importlib_metadata.__version__)

    @staticmethod
    def _test_files(files_iter):
        assert isinstance(files_iter, Iterator)
        files = list(files_iter)
        root = files[0].root
        for file in files:
            assert file.root == root
            assert not file.hash or file.hash.value
            assert not file.hash or file.hash.mode == 'sha256'
            assert not file.size or file.size >= 0
            assert file.locate().exists()
            assert isinstance(file.read_binary(), bytes)
            if file.name.endswith('.py'):
                file.read_text()

    def test_file_hash_repr(self):
        try:
            assertRegex = self.assertRegex
        except AttributeError:
            # Python 2
            assertRegex = self.assertRegexpMatches

        util = [
            p for p in importlib_metadata.files('wheel')
            if p.name == 'util.py'
            ][0]
        assertRegex(
            repr(util.hash),
            '<FileHash mode: sha256 value: .*>')

    def test_files_dist_info(self):
        self._test_files(importlib_metadata.files('pip'))

    def test_files_egg_info(self):
        self._test_files(importlib_metadata.files('importlib_metadata'))

    def test_find_local(self):
        dist = importlib_metadata.api.local_distribution()
        assert dist.metadata['Name'] == 'importlib-metadata'

    def test_requires(self):
        deps = importlib_metadata.requires('importlib_metadata')
        parsed = list(map(packaging.requirements.Requirement, deps))
        assert all(parsed)
        assert any(
            dep.name == 'pathlib2' and dep.marker
            for dep in parsed
            )

    def test_requires_dist_info(self):
        # assume 'packaging' is installed as a wheel with dist-info
        deps = importlib_metadata.requires('packaging')
        parsed = list(map(packaging.requirements.Requirement, deps))
        assert parsed

    def test_more_complex_deps_requires_text(self):
        requires = textwrap.dedent("""
            dep1
            dep2

            [:python_version < "3"]
            dep3

            [extra1]
            dep4

            [extra2:python_version < "3"]
            dep5
            """)
        deps = sorted(
            importlib_metadata.api.Distribution._deps_from_requires_text(
                requires)
            )
        expected = [
            'dep1',
            'dep2',
            'dep3; python_version < "3"',
            'dep4; extra == "extra1"',
            'dep5; (python_version < "3") and extra == "extra2"',
            ]
        # It's important that the environment marker expression be
        # wrapped in parentheses to avoid the following 'and' binding more
        # tightly than some other part of the environment expression.

        assert deps == expected
        assert all(map(packaging.requirements.Requirement, deps))
