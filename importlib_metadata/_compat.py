import sys
import platform

from typing import TypeVar


__all__ = ['install', 'NullFinder', 'PyPy_repr', 'Protocol', 'SupportsIndex']


if sys.version_info >= (3, 8):
    from typing import Protocol, SupportsIndex
else:
    from typing_extensions import Protocol, SupportsIndex


TypeT = TypeVar('TypeT', bound=type)


def install(cls: TypeT) -> TypeT:
    """
    Class decorator for installation on sys.meta_path.

    Adds the backport DistributionFinder to sys.meta_path and
    attempts to disable the finder functionality of the stdlib
    DistributionFinder.
    """
    sys.meta_path.append(cls())
    disable_stdlib_finder()
    return cls


def disable_stdlib_finder() -> None:
    """
    Give the backport primacy for discovering path-based distributions
    by monkey-patching the stdlib O_O.

    See #91 for more background for rationale on this sketchy
    behavior.
    """

    def matches(finder: object) -> bool:
        return getattr(
            finder, '__module__', None
        ) == '_frozen_importlib_external' and hasattr(finder, 'find_distributions')

    for finder in filter(matches, sys.meta_path):  # pragma: nocover
        del finder.find_distributions  # type: ignore[attr-defined]


class NullFinder:
    """
    A "Finder" (aka "MetaClassFinder") that never finds any modules,
    but may find distributions.
    """

    @staticmethod
    def find_spec(*args: object, **kwargs: object) -> None:
        return None

    # In Python 2, the import system requires finders
    # to have a find_module() method, but this usage
    # is deprecated in Python 3 in favor of find_spec().
    # For the purposes of this finder (i.e. being present
    # on sys.meta_path but having no other import
    # system functionality), the two methods are identical.
    find_module = find_spec


class PyPy_repr:
    """
    Override repr for EntryPoint objects on PyPy to avoid __iter__ access.
    Ref #97, #102.
    """

    affected = hasattr(sys, 'pypy_version_info')

    def __compat_repr__(self) -> str:  # pragma: nocover
        def make_param(name: str) -> str:
            value = getattr(self, name)
            return f'{name}={value!r}'

        params = ', '.join(map(make_param, self._fields))  # type: ignore[attr-defined]
        return f'EntryPoint({params})'

    if affected:  # pragma: nocover
        __repr__ = __compat_repr__
    del affected


def pypy_partial(val: int) -> int:
    """
    Adjust for variable stacklevel on partial under PyPy.

    Workaround for #327.
    """
    is_pypy = platform.python_implementation() == 'PyPy'
    return val + is_pypy
