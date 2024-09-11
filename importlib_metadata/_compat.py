from __future__ import annotations

import email.message
import importlib.metadata
import platform
import sys
import warnings
from typing import cast

import importlib_metadata._adapters


__all__ = ['install', 'NullFinder']


def install(cls):
    """
    Class decorator for installation on sys.meta_path.

    Adds the backport DistributionFinder to sys.meta_path and
    attempts to disable the finder functionality of the stdlib
    DistributionFinder.
    """
    sys.meta_path.append(cls())
    disable_stdlib_finder()
    return cls


def disable_stdlib_finder():
    """
    Give the backport primacy for discovering path-based distributions
    by monkey-patching the stdlib O_O.

    See #91 for more background for rationale on this sketchy
    behavior.
    """

    def matches(finder):
        return getattr(
            finder, '__module__', None
        ) == '_frozen_importlib_external' and hasattr(finder, 'find_distributions')

    for finder in filter(matches, sys.meta_path):  # pragma: nocover
        del finder.find_distributions


class NullFinder:
    """
    A "Finder" (aka "MetaPathFinder") that never finds any modules,
    but may find distributions.
    """

    @staticmethod
    def find_spec(*args, **kwargs):
        return None


def pypy_partial(val):
    """
    Adjust for variable stacklevel on partial under PyPy.

    Workaround for #327.
    """
    is_pypy = platform.python_implementation() == 'PyPy'
    return val + is_pypy


def localize_dist(
    dist: importlib_metadata.Distribution | importlib.metadata.Distribution,
) -> importlib_metadata.Distribution:
    """
    Ensure dist is an :class:`importlib_metadata.Distribution`.
    """
    if isinstance(dist, importlib_metadata.Distribution):
        return dist
    if isinstance(dist, importlib.metadata.PathDistribution):
        return importlib_metadata.PathDistribution(
            cast(importlib_metadata._meta.SimplePath, dist._path)
        )
    warnings.warn(f"Unrecognized distribution subclass {dist.__class__}")
    return cast(importlib_metadata.Distribution, dist)


def localize_metadata(
    input: importlib_metadata._adapters.Message | email.message.Message,
) -> importlib_metadata._adapters.Message:
    if isinstance(input, importlib_metadata._adapters.Message):
        return input
    return importlib_metadata._adapters.Message(input)


def localize_package_path(
    input: importlib_metadata.PackagePath | importlib.metadata.PackagePath,
) -> importlib_metadata.PackagePath:
    if isinstance(input, importlib_metadata.PackagePath):
        return input
    replacement = importlib_metadata.PackagePath(input)
    vars(replacement).update(vars(input))
    return replacement
