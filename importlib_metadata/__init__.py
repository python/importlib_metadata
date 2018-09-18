import sys

from .api import Distribution, PackageNotFoundError              # noqa: F401
from importlib import import_module

from . import _common
from ._common import entry_points

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


def _install():
    """Install the appropriate sys.meta_path finder for the Python version."""
    sys.meta_path.append(_common.MetadataPathFinder)
    sys.meta_path.append(_common.WheelMetadataFinder)


_install()

__version__ = version(__name__)
