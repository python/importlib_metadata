import os
import sys
import glob
import email
import itertools
import contextlib


class Distribution:
    def __init__(self, path):
        """
        Construct a distribution from a path to the metadata dir
        """
        self.path = path

    @classmethod
    def for_name(cls, name, path=sys.path):
        for path_item in path:
            glob_specs = (
                os.path.join(path_item, f'{name}-*.*-info'),
                os.path.join(path_item, f'{name}.*-info'),
                )
            globs = itertools.chain.from_iterable(map(glob.iglob, glob_specs))
            match = next(globs)
            return cls(os.path.join(path_item, match))

    @classmethod
    def for_module(cls, mod):
        return cls.for_name(cls.name_for_module(mod))

    @staticmethod
    def name_for_module(mod):
        return getattr(mod, '__dist_name__', mod.__name__)

    @property
    def metadata(self):
        return email.message_from_string(
            self.load_metadata('METADATA') or self.load_metadata('PKG-INFO')
            )

    def load_metadata(self, name):
        fn = os.path.join(self.path, name)
        with contextlib.suppress(FileNotFoundError):
            with open(fn, encoding='utf-8') as strm:
                return strm.read()

    @property
    def version(self):
        return self.metadata['Version']
