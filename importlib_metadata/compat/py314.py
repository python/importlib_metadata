import sys

native_lazy_imports = sys.version_info >= (3, 15)
"""
Whether the interpreter honors ``__lazy_modules__`` itself (PEP 810).
"""


class nothing:
    """
    A context that does nothing, the interpreter deferring the imports itself.
    """

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        return False


def backport():  # pragma: no cover
    """
    Borrow lazy_importer's emulation of PEP 810.
    """
    from lazy_importer import lazy_importer

    return lazy_importer()


def itself(value):
    """
    The value as bound, the interpreter having resolved it already.
    """
    return value


def resolved(value):  # pragma: no cover
    """
    The object the backport's proxy stands for.
    """
    from lazy_importer import resolve

    return resolve(value)


lazy_importer = nothing if native_lazy_imports else backport

resolve = itself if native_lazy_imports else resolved
"""
Supply a lazy name where the object itself is what matters.

A proxy passes attribute access and calls through to the object it
stands for, so most uses of a lazy name need nothing. ``isinstance``
and other operations on the object itself see the proxy, and silently
get the wrong answer, so those must resolve the name first.
"""
