from .api import Distribution, PackageNotFoundError              # noqa: F401
from .api import distribution, entry_points, resolve, version
from ._common import _install

__all__ = [
    'distribution',
    'entry_points',
    'resolve',
    'version',
    ]

_install()

__version__ = version(__name__)
