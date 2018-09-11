from ._py3 import PackageNotFound                   # noqa: F401
from ._py3 import Distribution
from configparser import ConfigParser
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


def entry_points(name):
    as_string = distribution(name).load_metadata('entry_points.txt')
    # 2018-09-10(barry): Should we provide any options here, or let the caller
    # send options to the underlying ConfigParser?   For now, YAGNI.
    config = ConfigParser()
    config.read_string(as_string)
    return config
