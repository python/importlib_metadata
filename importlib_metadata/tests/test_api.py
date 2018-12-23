import re
import textwrap
import unittest
import importlib_metadata
import packaging.requirements

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
        importlib_metadata.read_text('importlib_metadata', 'top_level.txt')

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

    def test_requires(self):
        deps = importlib_metadata.requires('importlib_metadata')
        parsed = list(map(packaging.requirements.Requirement, deps))
        assert all(parsed)
        assert any(
            dep.name == 'pathlib2' and dep.marker
            for dep in parsed
            )

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
        deps = list(
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
