from .api import Distribution, PackageNotFoundError  # noqa: F401
from .api import distribution, entry_points, resolve, version, read_text

# Import for installation side-effects.
from . import _hooks  # noqa: F401


__all__ = [
    'distribution',
    'entry_points',
    'resolve',
    'version',
    'read_text',
    ]


__version__ = version(__name__)
