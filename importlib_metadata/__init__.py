from .api import (
    Distribution, PackageNotFoundError, distribution, distributions,
    entry_points, files, metadata, requires, version)

# Import for installation side-effects.
__import__('importlib_metadata._hooks')


__all__ = [
    'Distribution',
    'PackageNotFoundError',
    'distribution',
    'distributions',
    'entry_points',
    'files',
    'metadata',
    'requires',
    'version',
    ]


__version__ = version(__name__)
