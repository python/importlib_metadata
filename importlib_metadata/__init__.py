import sys

from .api import Distribution, PackageNotFound      # noqa: F401
from types import ModuleType

if sys.version_info < (3, ):                      # pragma: nocover
    from ._py2 import entry_points
else:
    from ._py3 import entry_points                # noqa: F401 pragma: nocover


__all__ = [
    'distribution',
    'entry_points',
    'version',
    ]


def distribution(package):
    if isinstance(package, ModuleType):
        return Distribution.from_module(package)
    else:
        return Distribution.from_name(package)


def version(name):
    return distribution(name).version


def _install():                                     # pragma: nocover
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
