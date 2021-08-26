from typing import Any, DefaultDict, NamedTuple, Optional, TypeVar


# from jaraco.collections 3.3
K = TypeVar('K')
V = TypeVar('V')


class FreezableDefaultDict(DefaultDict[K, V]):
    """
    Often it is desirable to prevent the mutation of
    a default dict after its initial construction, such
    as to prevent mutation during iteration.

    >>> dd = FreezableDefaultDict(list)
    >>> dd[0].append('1')
    >>> dd.freeze()
    >>> dd[1]
    []
    >>> len(dd)
    1
    """

    def __missing__(self, key: K) -> V:
        return getattr(  # type: ignore[no-any-return]
            self, '_frozen', super().__missing__
        )(key)

    def freeze(self) -> None:
        if self.default_factory is not None:
            self._frozen = lambda key: self.default_factory()


class Pair(NamedTuple):
    name: Optional[str]
    value: Any  # Python 3.6 doesn't support generic NamedTuple

    @classmethod
    def parse(cls, text: str) -> 'Pair':
        return cls(*map(str.strip, text.split("=", 1)))
