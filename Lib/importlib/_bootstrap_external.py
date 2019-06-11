import sys


# Merge the body of this class into _bootstrap_external:
class PathFinder:
    search_template = r'(?:{pattern}(-.*)?\.(dist|egg)-info|EGG-INFO)'

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
        from pathlib import Path
        with suppress(Exception):
            return zipfile.Path(path)
        return Path(path)

    @classmethod
    def _predicate(cls, pattern, root, item):
        import re
        return re.match(pattern, str(item.name), flags=re.IGNORECASE)

    @classmethod
    def _search_path(cls, root, pattern):
        if not root.is_dir():
            return ()
        normalized = pattern.replace('-', '_')
        matcher = cls.search_template.format(pattern=normalized)
        return (item for item in root.iterdir()
                if cls._predicate(matcher, root, item))
