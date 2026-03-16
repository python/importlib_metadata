from __future__ import annotations

import email.message
import importlib.metadata
import warnings
from typing import cast

import importlib_metadata._adapters


def dist(
    dist: importlib_metadata.Distribution | importlib.metadata.Distribution,
) -> importlib_metadata.Distribution:
    """
    Ensure dist is an :class:`importlib_metadata.Distribution`.

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
    if isinstance(dist, importlib.metadata.PathDistribution):
        return importlib_metadata.PathDistribution(
            cast(importlib_metadata._meta.SimplePath, dist._path)
        )
    # workaround for when pytest has replaced importlib_metadata
    # https://github.com/python/importlib_metadata/pull/505#issuecomment-2344329001
    if dist.__class__.__module__ != 'importlib_metadata':
        warnings.warn(f"Unrecognized distribution subclass {dist.__class__}")
    return cast(importlib_metadata.Distribution, dist)


def message(
    input: importlib_metadata._adapters.Message | email.message.Message,
) -> importlib_metadata._adapters.Message:
    """
    Ensure a message is adapted to an importlib_metadata.Message.

    >>> stdlib = email.message.Message()
    >>> local = message(stdlib)
    >>> type(local)
    <class 'importlib_metadata._adapters.Message'>
    """
    if isinstance(input, importlib_metadata._adapters.Message):
        return input
    return importlib_metadata._adapters.Message(input)


def package_path(
    input: importlib_metadata.PackagePath | importlib.metadata.PackagePath,
) -> importlib_metadata.PackagePath:
    """
    Ensure a package path is adapted to an importlib_metadata.PackagePath.

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
