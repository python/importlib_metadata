from __future__ import absolute_import


import abc

from importlib.abc import MetaPathFinder


def abstractclassmethod(func):
    return classmethod(abc.abstractmethod(func))


class DistributionFinder(MetaPathFinder):
    """
    A MetaPathFinder capable of discovering installed distributions.
    """

    @abstractclassmethod
    def find_distributions(cls, name=None, path=None):
        """
        Return an iterable of all Distribution instances capable of
        loading the metadata for packages matching the name
        (or all names if not supplied) along the paths in the list
        of directories ``path`` (defaults to sys.path).
        """
