import contextlib

from jaraco.test.cpython import from_test_support, try_import

import_helper = try_import('import_helper') or from_test_support(
    'modules_setup', 'modules_cleanup'
)


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
