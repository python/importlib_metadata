import sys


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


lazy_importer = nothing if sys.version_info >= (3, 15) else backport
"""
Defer the imports in the block that follows, before 3.15 as after.

Two properties of the emulation shape how a module may declare its lazy
imports. Neither holds from 3.15, which defers them natively.

A lazy name is bound to a proxy. Attribute access and calls reach the
object it stands for, so ``csv.reader`` and ``_adapters.Message`` behave,
but ``isinstance`` and anything else handed the object itself see the
proxy and get the wrong answer in silence. Reach such an object through
a module (``_adapters.Message``), or resolve the name with
``lazy_importer.resolve`` before testing it.

``from . import <submodule>`` names the package as the module to defer.
That is fine from another module, but in the package's own ``__init__``
the proxy stands for the module being executed and resolves itself
through the globals entry that is the proxy, until the stack is
exhausted. Import the member there instead.
"""
