from __future__ import annotations

import warnings
from typing import TYPE_CHECKING, cast

import importlib_metadata

if TYPE_CHECKING:
    import email.message
    import importlib.metadata

    from .. import _adapters
    from .._meta import SimplePath


def dist(
    dist: importlib_metadata.Distribution | importlib.metadata.Distribution,
) -> importlib_metadata.Distribution:
    """
    Ensure dist is an :class:`importlib_metadata.Distribution`.

    >>> import importlib.metadata
    >>> stdlib = importlib.metadata.PathDistribution('foo')
    >>> type(stdlib)
    <class 'importlib.metadata.PathDistribution'>
    >>> local = dist(stdlib)
    >>> type(local)
    <class 'importlib_metadata.PathDistribution'>

    >>> class CustomDist(importlib.metadata.Distribution):
    ...     def read_text(self, name):
    ...         return
    ...     def locate_file(self, name):
    ...         return
    >>> subclass = CustomDist()
    >>> type(subclass)
    <class 'importlib_metadata._compat.localize.CustomDist'>
    >>> import pytest
    >>> with pytest.warns(UserWarning, match="Unrecognized distribution subclass <class 'importlib_metadata._compat.localize.CustomDist'>"):
    ...     local = dist(subclass)
    >>> type(local) is type(subclass)
    True
    """
    if isinstance(dist, importlib_metadata.Distribution):
        return dist

    # only a foreign dist gets this far, so defer the cost of the import
    # (python/cpython#109829)
    import importlib.metadata

    if isinstance(dist, importlib.metadata.PathDistribution):
        return importlib_metadata.PathDistribution(cast('SimplePath', dist._path))
    # workaround for when pytest has replaced importlib_metadata
    # https://github.com/python/importlib_metadata/pull/505#issuecomment-2344329001
    if dist.__class__.__module__ != 'importlib_metadata':
        warnings.warn(f"Unrecognized distribution subclass {dist.__class__}")
    return cast('importlib_metadata.Distribution', dist)


def message(
    input: _adapters.Message | email.message.Message,
) -> _adapters.Message:
    """
    Ensure a message is adapted to an importlib_metadata.Message.

    >>> import email.message
    >>> stdlib = email.message.Message()
    >>> local = message(stdlib)
    >>> type(local)
    <class 'importlib_metadata._adapters.Message'>
    """
    # deferred for performance (python/cpython#109829)
    from .. import _adapters

    if isinstance(input, _adapters.Message):
        return input
    return _adapters.Message(input)


def package_path(
    input: importlib_metadata.PackagePath | importlib.metadata.PackagePath,
) -> importlib_metadata.PackagePath:
    """
    Ensure a package path is adapted to an importlib_metadata.PackagePath.

    >>> import importlib.metadata
    >>> stdlib = importlib.metadata.PackagePath('foo')
    >>> type(stdlib)
    <class 'importlib.metadata.PackagePath'>
    >>> local = package_path(stdlib)
    >>> type(local)
    <class 'importlib_metadata.PackagePath'>
    """
    if isinstance(input, importlib_metadata.PackagePath):
        return input
    replacement = importlib_metadata.PackagePath(input)
    vars(replacement).update(vars(input))
    return replacement
