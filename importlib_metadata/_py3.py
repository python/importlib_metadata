import os
import re
import abc
import sys
import email
import pathlib
import itertools
import contextlib
import importlib


class PackageNotFound(Exception):
    """Package Not Found"""


@sys.meta_path.append                               # type: ignore
class MetadataPathFinder:
    """
    A degenerate finder, supplying only a find_distribution
    method for versions of Python that do not have a
    PathFinder find_distribution.
    """
    @staticmethod
    def find_spec(*args, **kwargs):
        return None

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
            for path in map(pathlib.Path, sys.path)
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
            and re.match(rf'{name}(-.*)?\.(dist|egg)-info', str(item.name))
            )


class Distribution:
    """
    A Python Distribution package.
    """

    @abc.abstractmethod
    def load_metadata(self, name):
        """
        Attempt to load metadata given by the name. Return None if not found.
        """

    @classmethod
    def from_name(cls, name):
        """
        Given the name of a distribution (the name of the package as
        installed), return a Distribution.
        """
        for resolver in cls._discover_resolvers():
            resolved = resolver(name)
            if resolved is not None:
                return resolved
        else:
            raise PackageNotFound(name)

    @staticmethod
    def _discover_resolvers():
        """
        Search the meta_path for resolvers.
        """
        declared = (
            getattr(finder, 'find_distribution', None)
            for finder in sys.meta_path
            )
        return filter(None, declared)

    @classmethod
    def from_module(cls, mod):
        """
        Given a module, discover the Distribution package for that
        module.
        """
        return cls.from_name(cls.name_for_module(mod))

    @classmethod
    def from_named_module(cls, mod_name):
        return cls.from_module(importlib.import_module(mod_name))

    @staticmethod
    def name_for_module(mod):
        """
        Given an imported module, infer the distribution package name.
        """
        return getattr(mod, '__dist_name__', mod.__name__)

    @property
    def metadata(self):
        """
        Return metadata for this Distribution, parsed.
        """
        return email.message_from_string(
            self.load_metadata('METADATA') or self.load_metadata('PKG-INFO')
            )

    @property
    def version(self):
        return self.metadata['Version']


class PathDistribution(Distribution):
    def __init__(self, path):
        """
        Construct a distribution from a path to the metadata dir.
        """
        self.path = path

    def load_metadata(self, name):
        """
        Attempt to load metadata given by the name. Return None if not found.
        """
        fn = os.path.join(self.path, name)
        with contextlib.suppress(FileNotFoundError):
            with open(fn, encoding='utf-8') as strm:
                return strm.read()
