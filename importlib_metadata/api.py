import abc
import sys
import email
import importlib


try:
    BaseClass = ModuleNotFoundError
except NameError:                                 # pragma: nocover
    BaseClass = ImportError                       # type: ignore


class PackageNotFoundError(BaseClass):
    """The package was not found."""


class Distribution:
    """A Python distribution package."""

    @abc.abstractmethod
    def load_metadata(self, name):
        """Attempt to load metadata given by the name.

        :param name: The name of the distribution package.
        :return: The metadata string if found, otherwise None.
        """

    @classmethod
    def from_name(cls, name):
        """Return the Distribution for the given package name.

        :param name: The name of the distribution package to search for.
        :return: The Distribution instance (or subclass thereof) for the named
            package, if found.
        :raises PackageNotFoundError: When the named package's distribution
            metadata cannot be found.
        """
        for resolver in cls._discover_resolvers():
            resolved = resolver(name)
            if resolved is not None:
                return resolved
        else:
            raise PackageNotFoundError(name)

    @staticmethod
    def _discover_resolvers():
        """Search the meta_path for resolvers."""
        declared = (
            getattr(finder, 'find_distribution', None)
            for finder in sys.meta_path
            )
        return filter(None, declared)

    @classmethod
    def from_module(cls, module):
        """Discover the Distribution package for a module."""
        return cls.from_name(cls.name_for_module(module))

    @classmethod
    def from_named_module(cls, mod_name):
        return cls.from_module(importlib.import_module(mod_name))

    @staticmethod
    def name_for_module(module):
        """Given an imported module, infer the distribution package name."""
        return getattr(module, '__dist_name__', module.__name__)

    @property
    def metadata(self):
        """Return the parsed metadata for this Distribution.

        The returned object will have keys that name the various bits of
        metadata.  See PEP 566 for details.
        """
        return email.message_from_string(
            self.load_metadata('METADATA') or self.load_metadata('PKG-INFO')
            )

    @property
    def version(self):
        """Return the 'Version' metadata for the distribution package."""
        return self.metadata['Version']
