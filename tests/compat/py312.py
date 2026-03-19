import contextlib

from test.support import import_helper  # type: ignore[import-untyped]


@contextlib.contextmanager
def isolated_modules():
    """
    Save modules on entry and cleanup on exit.
    """
    (saved,) = import_helper.modules_setup()
    try:
        yield
    finally:
        import_helper.modules_cleanup(saved)


vars(import_helper).setdefault('isolated_modules', isolated_modules)
