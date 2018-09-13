import os
import re
import sys
import errno
import codecs
import itertools

from .api import Distribution
from ConfigParser import SafeConfigParser
from cStringIO import StringIO
from importlib import import_module
from pathlib2 import Path
from zipfile import ZipFile


class MetadataPathFinder:
    """A degenerate finder for distribution packages.

    This finder supplies only a find_distribution() method for versions
    of Python that do not have a PathFinder find_distribution().
    """
    @staticmethod
    def find_module(*args, **kwargs):
        return None

    @classmethod
    def find_distribution(cls, name):
        paths = cls._search_paths(name)
        dists = map(PathDistribution, paths)
        if len(dists) > 0:
            return dists[0]
        return None

    @classmethod
    def _search_paths(cls, name):
        return itertools.chain.from_iterable(
            cls._search_path(path, name)
            for path in map(Path, sys.path)
            )

    @classmethod
    def _search_path(cls, root, name):
        if root.is_dir():
            for item in root.iterdir():
                item_name = str(item.name)
                if (item.is_dir()
                    and item_name.startswith(name)
                    and re.match(r'{}(-.*)?\.(dist|egg)-info'.format(name),
                                 item_name)):
                    yield item


class WheelMetadataFinder:
    """A degenerate finder for distribution packages in wheels.

    This finder supplies only a find_distribution() method for versions
    of Python that do not have a PathFinder find_distribution().
    """
    @staticmethod
    def find_module(*args, **kwargs):
        return None

    @classmethod
    def find_distribution(cls, name):
        try:
            module = import_module(name)
        except ImportError:
            return None
        loader = getattr(module, '__loader__', None)
        if loader is None:
            return
        archive = loader.archive
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


class PathDistribution(Distribution):
    def __init__(self, path):
        """Construct a distribution from a path to the metadata directory."""
        self.path = path

    def load_metadata(self, name):
        """Attempt to load metadata given by the name.

        :param name: The name of the distribution package.
        :return: The metadata string if found, otherwise None.
        """
        filename = os.path.join(str(self.path), name)
        try:
            with codecs.open(filename, encoding='utf-8') as fp:
                return fp.read()
        except IOError as error:
            if error.errno != errno.ENOENT:
                raise                               # pragma: nocover
            return None


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
            try:
                as_bytes = zf.read('{}/{}'.format(self._dist_info, name))
            except KeyError:
                return None
            return as_bytes.decode('utf-8')


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
    config = SafeConfigParser()
    config.readfp(StringIO(as_string))
    return config
