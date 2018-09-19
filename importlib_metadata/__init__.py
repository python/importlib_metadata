from importlib import import_module

from .api import Distribution, PackageNotFoundError              # noqa: F401
from .api import distribution, entry_points, resolve, version

__all__ = [
    'distribution',
    'entry_points',
    'resolve',
    'version',
    ]

import_module('._common', __package__)

__version__ = version(__name__)
