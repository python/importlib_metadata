import contextlib
import sys
import types
import warnings
from collections.abc import Mapping

from test.support import warnings_helper as orig

if sys.version_info >= (3, 15):
    from builtins import frozendict
else:

    class frozendict(Mapping):
        """
        Approximate frozendict, added to builtins in Python 3.15.

        Accepts anything dict() accepts and presents it read-only.

        >>> frozendict(a=1)['a']
        1
        >>> frozendict({'a': 1}) == {'a': 1}
        True
        >>> frozendict(a=1)
        frozendict({'a': 1})

        Hashable when the values are.

        >>> hash(frozendict(a=1)) == hash(frozendict(a=1))
        True

        Unlike a mapping proxy, supports copying, so callers may take a
        mutable snapshot to alter.

        >>> import copy
        >>> spec = frozendict(pkg={'META': 'lower'})
        >>> altered = copy.deepcopy(spec)
        >>> altered['pkg']['META'] = 'UPPER'
        >>> spec['pkg']['META']
        'lower'
        """

        def __init__(self, *args, **kwargs):
            self._data = dict(*args, **kwargs)

        def __getitem__(self, key):
            return self._data[key]

        def __iter__(self):
            return iter(self._data)

        def __len__(self):
            return len(self._data)

        def __hash__(self):
            return hash(frozenset(self._data.items()))

        def __repr__(self):
            return f'{type(self).__name__}({self._data!r})'


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
