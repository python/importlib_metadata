import os
import re
import sys
import errno
import codecs
import itertools

from .api import Distribution
from ConfigParser import SafeConfigParser
from cStringIO import StringIO
from pathlib2 import Path


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
