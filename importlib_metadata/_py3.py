import os
import sys
import glob
import email
import itertools
import contextlib
import importlib


class PackageNotFound(Exception):
    """Package Not Found"""


class Distribution:
    """
    A Python Distribution package.
    """

    def __init__(self, path):
        """
        Construct a distribution from a path to the metadata dir.
        """
        self.path = path

    @classmethod
    def from_name(cls, name):
        """
        Given the name of a distribution (the name of the package as
        installed), return a Distribution.
        """
        glob_groups = map(glob.iglob, cls._search_globs(name))
        globs = itertools.chain.from_iterable(glob_groups)
        try:
            dist_path = next(globs)
        except StopIteration:
            raise PackageNotFound
        return cls(dist_path)

    @staticmethod
    def _search_globs(name):
        """
        Generate search globs for locating distribution metadata in path.
        """
        for path_item in sys.path:
            # Matches versioned dist-info directories.
            yield os.path.join(path_item, f'{name}-*.*-info')
            # In develop install, no version is present in the egg-info
            # directory name.
            yield os.path.join(path_item, f'{name}.*-info')

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

    def load_metadata(self, name):
        """
        Attempt to load metadata given by the name. Return None if not found.
        """
        fn = os.path.join(self.path, name)
        with contextlib.suppress(FileNotFoundError):
            with open(fn, encoding='utf-8') as strm:
                return strm.read()

    @property
    def version(self):
        return self.metadata['Version']
