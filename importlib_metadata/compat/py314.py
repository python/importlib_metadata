import sys


class native:
    """
    A context that does nothing, as the interpreter defers the imports itself.
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


# Python 3.15 honors __lazy_modules__ natively (PEP 810); only earlier
# versions need the imports routed through the backport.
lazy_importer = native if sys.version_info >= (3, 15) else backport
