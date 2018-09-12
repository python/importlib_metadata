import sys

from .api import Distribution, PackageNotFound      # noqa: F401
from importlib import import_module
from types import ModuleType

if sys.version_info < (3, ):                      # pragma: nocover
    from ._py2 import entry_points
else:
    from ._py3 import entry_points                # noqa: F401 pragma: nocover


__all__ = [
    'distribution',
    'entry_points',
    'resolve',
    'version',
    ]


def distribution(package):
    """Get the ``Distribution`` instance for the given package.

    :param package: The module object for the package or the name of the
        package as a string.
    :return: A ``Distribution`` instance (or subclass thereof).
    """
    if isinstance(package, ModuleType):
        return Distribution.from_module(package)
    else:
        return Distribution.from_name(package)


def version(package):
    """Get the version string for the named package.

    :param package: The module object for the package or the name of the
        package as a string.
    :return: The version string for the package as defined in the package's
        "Version" metadata key.
    """
    return distribution(package).version


def resolve(entry_point):
    """Resolve an entry point string into the named callable.

    :param entry_point: An entry point string of the form
        `path.to.module:callable`.
    :return: The actual callable object `path.to.module.callable`
    :raises ValueError: When `entry_point` doesn't have the proper format.
    """
    path, colon, name = entry_point.rpartition(':')
    if colon != ':':
        raise ValueError('Not an entry point: {}'.format(entry_point))
    module = import_module(path)
    return getattr(module, name)


def _install():                                     # pragma: nocover
    """Install the appropriate sys.meta_path finder for the Python version."""
    if sys.version_info < (3, ):
        from ._py2 import MetadataPathFinder
        sys.meta_path.append(MetadataPathFinder)
    # XXX Until we port the API into Python 3.8, use importlib_metadata.
    elif sys.version_info < (3, 9):
        from ._py3 import MetadataPathFinder
        sys.meta_path.append(MetadataPathFinder)
    else:
        pass


_install()
