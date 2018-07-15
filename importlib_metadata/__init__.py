import sys

from ._py3 import PackageNotFound                   # noqa: F401
from ._py3 import Distribution
from types import ModuleType


__all__ = [
    'distribution',
    'version',
    ]


def distribution(package, search_path=None):
    if isinstance(package, ModuleType):
        return Distribution.from_module(package)
    else:
        return Distribution.from_name(
            package,
            sys.path if search_path is None else search_path)


def version(name, search_path=None):
    return distribution(name, search_path).version
