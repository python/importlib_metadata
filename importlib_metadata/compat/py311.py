import operator
import os
import pathlib
import sys
import types
import typing


def wrap(path):  # pragma: no cover
    """
    Workaround for https://github.com/python/cpython/issues/84538
    to add backward compatibility for walk_up=True.
    An example affected package is dask-labextension, which uses
    jupyter-packaging to install JupyterLab javascript files outside
    of site-packages.
    """

    def relative_to(root, *, walk_up=False):
        return pathlib.Path(os.path.relpath(path, root))

    return types.SimpleNamespace(relative_to=relative_to)


relative_fix = wrap if sys.version_info < (3, 12) else lambda x: x


# __protocol_attrs__ is only present on Python 3.12 and later.
protocol_attrs = (
    typing._get_protocol_attrs  # type: ignore[attr-defined] # private, 3.11 only
    if sys.version_info < (3, 12)
    else operator.attrgetter('__protocol_attrs__')
)


def static_isinstance(instance, protocol):  # pragma: no cover
    """
    Determine protocol conformance from the type alone.

    Workaround for https://github.com/python/cpython/issues/102433.
    Through Python 3.11, isinstance() against a runtime-checkable
    protocol calls hasattr() on the instance, so deciding the question
    evaluates every property member and anything one raises propagates.
    Python 3.12 consults the type instead.
    """
    return all(hasattr(type(instance), attr) for attr in protocol_attrs(protocol))


conforms = static_isinstance if sys.version_info < (3, 12) else isinstance
