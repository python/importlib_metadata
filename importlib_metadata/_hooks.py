from __future__ import unicode_literals, absolute_import

import re
import sys
import zipp
import itertools

from .abc import DistributionFinder
from .api import Distribution


if sys.version_info >= (3,):  # pragma: nocover
    from contextlib import suppress
else:  # pragma: nocover
    from contextlib2 import suppress  # noqa
    from itertools import imap as map  # type: ignore

    FileNotFoundError = IOError, OSError
    NotADirectoryError = IOError, OSError
    __metaclass__ = type


if sys.version_info > (3, 5):  # pragma: nocover
    from pathlib import Path
else:  # pragma: nocover
    from pathlib2 import Path


def install(cls):
    """Class decorator for installation on sys.meta_path."""
    sys.meta_path.append(cls())
    return cls


class NullFinder(DistributionFinder):
    """
    A "Finder" (aka "MetaClassFinder") that never finds any modules,
    but may find distributions.
    """
    @staticmethod
    def find_spec(*args, **kwargs):
        return None

    # In Python 2, the import system requires finders
    # to have a find_module() method, but this usage
    # is deprecated in Python 3 in favor of find_spec().
    # For the purposes of this finder (i.e. being present
    # on sys.meta_path but having no other import
    # system functionality), the two methods are identical.
    find_module = find_spec


@install
class MetadataPathFinder(NullFinder):
    """A degenerate finder for distribution packages on the file system.

    This finder supplies only a find_distributions() method for versions
    of Python that do not have a PathFinder find_distributions().
    """
    search_template = r'(?:{pattern}(-.*)?\.(dist|egg)-info|EGG-INFO)'

    def find_distributions(self, name=None, path=None):
        """Return an iterable of all Distribution instances capable of
        loading the metadata for packages matching the name
        (or all names if not supplied) along the paths in the list
        of directories ``path`` (defaults to sys.path).
        """
        if path is None:
            path = sys.path
        pattern = '.*' if name is None else re.escape(name)
        found = self._search_paths(pattern, path)
        return map(PathDistribution, found)

    @classmethod
    def _search_paths(cls, pattern, paths):
        """
        Find metadata directories in paths heuristically.
        """
        return itertools.chain.from_iterable(
            cls._search_path(path, pattern)
            for path in map(cls._switch_path, paths)
            )

    @staticmethod
    def _switch_path(path):
        with suppress(Exception):
            return zipp.Path(path)
        return Path(path)

    @classmethod
    def _predicate(cls, pattern, root, item):
        return re.match(pattern, str(item.name), flags=re.IGNORECASE)

    @classmethod
    def _search_path(cls, root, pattern):
        if not root.is_dir():
            return ()
        normalized = pattern.replace('-', '_')
        matcher = cls.search_template.format(pattern=normalized)
        return (item for item in root.iterdir()
                if cls._predicate(matcher, root, item))


class PathDistribution(Distribution):
    def __init__(self, path):
        """Construct a distribution from a path to the metadata directory."""
        self._path = path

    def read_text(self, filename):
        with suppress(FileNotFoundError, NotADirectoryError, KeyError):
            return self._path.joinpath(filename).read_text(encoding='utf-8')
    read_text.__doc__ = Distribution.read_text.__doc__

    def locate_file(self, path):
        return self._path.parent / path
