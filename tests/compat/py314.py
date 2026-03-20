import contextlib
import sys
import types
import warnings

from test.support import warnings_helper as orig


@contextlib.contextmanager
def ignore_warnings(*, category, message=''):
    """Decorator to suppress warnings.

    Can also be used as a context manager. This is not preferred,
    because it makes diffs more noisy and tools like 'git blame' less useful.
    But, it's useful for async functions.
    """
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore', category=category, message=message)
        yield


@contextlib.contextmanager
def ignore_fork_in_thread_deprecation_warnings():
    """Suppress deprecation warnings related to forking in multi-threaded code.

    See gh-135427

    Can be used as decorator (preferred) or context manager.
    """
    with ignore_warnings(
        message=".*fork.*may lead to deadlocks in the child.*",
        category=DeprecationWarning,
    ):
        yield


if sys.version_info >= (3, 15):
    warnings_helper = orig
else:
    warnings_helper = types.SimpleNamespace(
        ignore_fork_in_thread_deprecation_warnings=ignore_fork_in_thread_deprecation_warnings,
        **vars(orig),
    )
