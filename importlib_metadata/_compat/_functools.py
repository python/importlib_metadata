"""
Functional helpers needed only by the backport.

``apply`` and ``compose`` exist to serve the localization decorators on
the public API, which the stdlib does not have. Keeping them out of
``_functools`` leaves that module identical to its
``importlib.metadata`` counterpart.
"""

import functools


# From jaraco.functools 4.0.2
def compose(*funcs):
    """
    Compose any number of unary functions into a single unary function.

    Comparable to
    `function composition <https://en.wikipedia.org/wiki/Function_composition>`_
    in mathematics:

    ``h = g ∘ f`` implies ``h(x) = g(f(x))``.

    In Python, ``h = compose(g, f)``.

    >>> import textwrap
    >>> expected = str.strip(textwrap.dedent(compose.__doc__))
    >>> strip_and_dedent = compose(str.strip, textwrap.dedent)
    >>> strip_and_dedent(compose.__doc__) == expected
    True

    Compose also allows the innermost function to take arbitrary arguments.

    >>> round_three = lambda x: round(x, ndigits=3)
    >>> f = compose(round_three, int.__truediv__)
    >>> [f(3*x, x+1) for x in range(1,10)]
    [1.5, 2.0, 2.25, 2.4, 2.5, 2.571, 2.625, 2.667, 2.7]
    """

    def compose_two(f1, f2):
        return lambda *args, **kwargs: f1(f2(*args, **kwargs))

    return functools.reduce(compose_two, funcs)


def apply(transform):
    """
    Decorate a function with a transform function that is
    invoked on results returned from the decorated function.

    >>> @apply(reversed)
    ... def get_numbers(start):
    ...     "doc for get_numbers"
    ...     return range(start, start+3)
    >>> list(get_numbers(4))
    [6, 5, 4]
    >>> get_numbers.__doc__
    'doc for get_numbers'
    """

    def wrap(func):
        return functools.wraps(func)(compose(transform, func))

    return wrap
