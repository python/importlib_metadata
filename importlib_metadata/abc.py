from __future__ import absolute_import


import abc
import sys

if sys.version_info >= (3,):  # pragma: nocover
    from importlib.abc import MetaPathFinder

    def abstractclassmethod(func):
        return classmethod(abc.abstractmethod(func))
else:  # pragma: nocover
    from abc import ABCMeta as MetaPathFinder

    class abstractclassmethod(classmethod):
        __isabstractmethod__ = True

        def __init__(self, callable):
            callable.__isabstractmethod__ = True
            super(abstractclassmethod, self).__init__(callable)


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
