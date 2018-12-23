from .api import distribution, Distribution, PackageNotFoundError  # noqa: F401
from .api import metadata, entry_points, version, read_text, requires

# Import for installation side-effects.
from . import _hooks  # noqa: F401


__all__ = [
    'metadata',
    'entry_points',
    'version',
    'read_text',
    'requires',
    ]


__version__ = version(__name__)
