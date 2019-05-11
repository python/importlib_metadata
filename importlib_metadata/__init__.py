from .api import (
    Distribution, PackageNotFoundError, distribution, distributions,
    entry_points, files, metadata, requires, version)


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
