import sys


__metaclass__ = type


def install(cls):
    """Class decorator for installation on sys.meta_path."""
    sys.meta_path.append(cls())
    return cls


class NullFinder:
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
