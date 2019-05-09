from .api import (
    distribution, Distribution, distributions, entry_points, files,
    metadata, PackageNotFoundError, requires, version,
    )

# Import for installation side-effects.
from . import _hooks  # noqa: F401


__all__ = [
    'distribution',
    'Distribution',
    'distributions',
    'entry_points',
    'files',
    'metadata',
    'PackageNotFoundError',
    'requires',
    'version',
    ]


__version__ = version(__name__)
