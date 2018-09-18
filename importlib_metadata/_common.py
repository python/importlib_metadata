from __future__ import unicode_literals, absolute_import

import io
import re
import sys
import itertools

from .api import Distribution
from importlib import import_module
from zipfile import ZipFile

if sys.version_info >= (3,):  # pragma: nocover
    from contextlib import suppress
    from configparser import ConfigParser
    from pathlib import Path
else:  # pragma: nocover
    from ConfigParser import SafeConfigParser as ConfigParser
    from contextlib2 import suppress  # noqa
    from itertools import imap as map  # type: ignore
    from pathlib2 import Path

    FileNotFoundError = IOError, OSError


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

    def load_metadata(self, name):
        """Attempt to load metadata given by the name.

        :param name: The name of the distribution package.
        :return: The metadata string if found, otherwise None.
        """
        with suppress(FileNotFoundError):
            with self._path.joinpath(name).open(encoding='utf-8') as fp:
                return fp.read()
        return None


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

    def load_metadata(self, name):
        """Attempt to load metadata given by the name.

        :param name: The name of the distribution package.
        :return: The metadata string if found, otherwise None.
        """
        if name == 'METADATA':
            return self._metadata
        with ZipFile(self._archive) as zf:
            with suppress(KeyError):
                as_bytes = zf.read('{}/{}'.format(self._dist_info, name))
                return as_bytes.decode('utf-8')
        return None


def entry_points(name):
    """Return the entry points for the named distribution package.

    :param name: The name of the distribution package to query.
    :return: A ConfigParser instance where the sections and keys are taken
        from the entry_points.txt ini-style contents.
    """
    # Avoid circular imports.
    from importlib_metadata import distribution
    as_string = distribution(name).load_metadata('entry_points.txt')
    # 2018-09-10(barry): Should we provide any options here, or let the caller
    # send options to the underlying ConfigParser?   For now, YAGNI.
    config = ConfigParser()
    try:
        config.read_string(as_string)
    except AttributeError:  # pragma: nocover
        # Python 2 has no read_string
        config.readfp(io.StringIO(as_string))
    return config
