from ._py3 import PackageNotFound                   # noqa: F401
from ._py3 import Distribution
from types import ModuleType


__all__ = [
    'distribution',
    'version',
    ]


def distribution(package):
    if isinstance(package, ModuleType):
        return Distribution.from_module(package)
    else:
        return Distribution.from_name(package)


def version(name):
    return distribution(name).version
