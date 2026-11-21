import collections
import typing


# from jaraco.collections 3.3
class FreezableDefaultDict(collections.defaultdict):
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

    def __missing__(self, key):
        if getattr(self, '_frozen', False):
            return self.default_factory()
        return super().__missing__(key)

    def freeze(self):
        self._frozen = True


class Pair(typing.NamedTuple):
    name: str
    value: str

    @classmethod
    def parse(cls, text):
        return cls(*map(str.strip, text.split("=", 1)))
