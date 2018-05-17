import os
import sys
import glob


class Distribution:
    def __init__(self, path):
        """
        Construct a distribution from a path to the metadata dir
        """
        self.path = path

    @classmethod
    def for_name(cls, name, path=sys.path):
        for path_item in path:
            glob_spec = os.path.join(path_item, f'{name}-*.dist-info')
            match = next(glob.iglob(glob_spec))
            return cls(os.path.join(path_item, match))

    @classmethod
    def for_module(cls, mod):
        return cls.for_name(cls.dist_name_for_module(mod))

    @staticmethod
    def name_for_module(mod):
        return getattr(mod, '__dist_name__', mod.__name__)
