import os
import sys
import glob
import email
import itertools
import contextlib


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
    def for_name(cls, name, path=sys.path):
        """
        Given the name of a distribution (the name of the package as
        installed), return a Distribution.
        """
        glob_groups = map(glob.iglob, cls._search_globs(name, path))
        globs = itertools.chain.from_iterable(glob_groups)
        return cls(next(globs))

    @staticmethod
    def _search_globs(name, path):
        """
        Generate search globs for locating distribution metadata in path.
        """
        for path_item in path:
                yield os.path.join(path_item, f'{name}-*.*-info')
                # in develop install, no version is present
                yield os.path.join(path_item, f'{name}.*-info')

    @classmethod
    def for_module(cls, mod):
        """
        Given a module, discover the Distribution package for that
        month.
        """
        return cls.for_name(cls.name_for_module(mod))

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
