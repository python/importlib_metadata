import abc
import sys
import email
import importlib


class PackageNotFound(Exception):
    """Package Not Found"""


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
