from __future__ import unicode_literals, absolute_import

import re
import sys
import itertools

from .api import Distribution
from importlib import import_module
from zipfile import ZipFile

if sys.version_info >= (3,):  # pragma: nocover
    from contextlib import suppress
    from pathlib import Path
else:  # pragma: nocover
    from contextlib2 import suppress  # noqa
    from itertools import imap as map  # type: ignore
    from pathlib2 import Path

    FileNotFoundError = IOError, OSError
    __metaclass__ = type


def install(cls):
    """Class decorator for installation on sys.meta_path."""
    sys.meta_path.append(cls)
    return cls


class NullFinder:
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

    This finder supplies only a find_distribution() method for versions
    of Python that do not have a PathFinder find_distribution().
    """

    @classmethod
    def find_distribution(cls, name):
        paths = cls._search_paths(name)
        dists = map(PathDistribution, paths)
        return next(dists, None)

    @classmethod
    def _search_paths(cls, name):
        """
        Find metadata directories in sys.path heuristically.
        """
        return itertools.chain.from_iterable(
            cls._search_path(path, name)
            for path in map(Path, sys.path)
            )

    @classmethod
    def _search_path(cls, root, name):
        if not root.is_dir():
            return ()
        return (
            item
            for item in root.iterdir()
            if item.is_dir()
            and str(item.name).startswith(name)
            and re.match(
                r'{name}(-.*)?\.(dist|egg)-info'.format(name=name),
                str(item.name),
                )
            )


class PathDistribution(Distribution):
    def __init__(self, path):
        """Construct a distribution from a path to the metadata directory."""
        self._path = path

    def read_text(self, filename):
        with suppress(FileNotFoundError):
            with self._path.joinpath(filename).open(encoding='utf-8') as fp:
                return fp.read()
        return None
    read_text.__doc__ = Distribution.read_text.__doc__


@install
class WheelMetadataFinder(NullFinder):
    """A degenerate finder for distribution packages in wheels.

    This finder supplies only a find_distribution() method for versions
    of Python that do not have a PathFinder find_distribution().
    """
    @classmethod
    def find_distribution(cls, name):
        try:
            module = import_module(name)
        except ImportError:
            return None

        # Python 2: allow modules without a loader.
        # Only modules with a __loader__.archive are relevant.
        loader = getattr(module, '__loader__', None)
        archive = getattr(loader, 'archive', None)
        if archive is None:
            return None

        try:
            name, version = Path(archive).name.split('-')[0:2]
        except ValueError:
            return None
        dist_info = '{}-{}.dist-info'.format(name, version)
        with ZipFile(archive) as zf:
            # Since we're opening the zip file anyway to see if there's a
            # METADATA file in the .dist-info directory, we might as well
            # read it and cache it here.
            zi = zf.getinfo('{}/{}'.format(dist_info, 'METADATA'))
            metadata = zf.read(zi).decode('utf-8')
        return WheelDistribution(archive, dist_info, metadata)


class WheelDistribution(Distribution):
    def __init__(self, archive, dist_info, metadata):
        self._archive = archive
        self._dist_info = dist_info
        self._metadata = metadata

    def read_text(self, filename):
        if filename == 'METADATA':
            return self._metadata
        with ZipFile(self._archive) as zf:
            with suppress(KeyError):
                as_bytes = zf.read('{}/{}'.format(self._dist_info, filename))
                return as_bytes.decode('utf-8')
        return None
    read_text.__doc__ = Distribution.read_text.__doc__
