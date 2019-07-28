import sys
import os


# Merge the body of this class into _bootstrap_external:
class PathFinder:
    @classmethod
    def find_distributions(cls, name=None, path=None):
        """
        Find distributions.

        Return an iterable of all Distribution instances capable of
        loading the metadata for packages matching the ``name``
        (or all names if not supplied) along the paths in the list
        of directories ``path`` (defaults to sys.path).
        """
        import re
        from importlib.metadata import PathDistribution
        if path is None:
            path = sys.path
        pattern = '.*' if name is None else re.escape(name)
        found = cls._search_paths(pattern, path)
        return map(PathDistribution, found)

    @classmethod
    def _search_paths(cls, pattern, paths):
        """Find metadata directories in paths heuristically."""
        import itertools
        return itertools.chain.from_iterable(
            cls._search_path(path, pattern)
            for path in map(cls._switch_path, paths)
            )

    @staticmethod
    def _switch_path(path):
        from contextlib import suppress
        import zipfile
        import pathlib
        PYPY_OPEN_BUG = False
        if not PYPY_OPEN_BUG or os.path.isfile(path):  # pragma: no branch
            with suppress(Exception):
                return zipfile.Path(path)
        return pathlib.Path(path)

    @classmethod
    def _matches_info(cls, normalized, item):
        import re
        template = r'{pattern}(-.*)?\.(dist|egg)-info'
        manifest = template.format(pattern=normalized)
        return re.match(manifest, item.name, flags=re.IGNORECASE)

    @classmethod
    def _matches_legacy(cls, normalized, item):
        import re
        template = r'{pattern}-.*\.egg[\\/]EGG-INFO'
        manifest = template.format(pattern=normalized)
        return re.search(manifest, str(item), flags=re.IGNORECASE)

    @classmethod
    def _search_path(cls, root, pattern):
        if not root.is_dir():
            return ()
        normalized = pattern.replace('-', '_')
        return (item for item in root.iterdir()
                if cls._matches_info(normalized, item)
                or cls._matches_legacy(normalized, item))
