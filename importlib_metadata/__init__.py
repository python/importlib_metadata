from .api import Distribution, PackageNotFoundError  # noqa: F401
from .api import distribution, entry_points, resolve, version

# Import for installation side-effects.
from . import _hooks  # noqa: F401


__all__ = [
    'distribution',
    'entry_points',
    'resolve',
    'version',
    ]


__version__ = version(__name__)
