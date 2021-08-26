from itertools import filterfalse
from typing import (
    Callable,
    Hashable,
    Iterable,
    Iterator,
    Optional,
    Set,
    TypeVar,
    overload,
)

T = TypeVar('T')
HashableT = TypeVar('HashableT', bound=Hashable)


@overload
def unique_everseen(
    iterable: Iterable[HashableT], key: None = ...
) -> Iterator[HashableT]:
    ...  # pragma: no cover


@overload
def unique_everseen(iterable: Iterable[T], key: Callable[[T], Hashable]) -> Iterator[T]:
    ...  # pragma: no cover


def unique_everseen(
    iterable: Iterable[T], key: Optional[Callable[[T], Hashable]] = None
) -> Iterator[T]:
    "List unique elements, preserving order. Remember all elements ever seen."
    # unique_everseen('AAAABBBCCDAABBB') --> A B C D
    # unique_everseen('ABBCcAD', str.lower) --> A B C D
    seen: Set[object] = set()
    seen_add = seen.add
    if key is None:
        for element in filterfalse(seen.__contains__, iterable):
            seen_add(element)
            yield element
    else:
        for element in iterable:
            k = key(element)
            if k not in seen:
                seen_add(k)
                yield element
