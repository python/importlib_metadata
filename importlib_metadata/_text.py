import re

from ._compat import SupportsIndex
from ._functools import method_cache
from typing import List, Optional


# from jaraco.text 3.5
class FoldedCase(str):
    """
    A case insensitive string class; behaves just like str
    except compares equal when the only variation is case.

    >>> s = FoldedCase('hello world')

    >>> s == 'Hello World'
    True

    >>> 'Hello World' == s
    True

    >>> s != 'Hello World'
    False

    >>> s.index('O')
    4

    >>> s.split('O')
    ['hell', ' w', 'rld']

    >>> s.split()
    ['hello', 'world']

    >>> sorted(map(FoldedCase, ['GAMMA', 'alpha', 'Beta']))
    ['alpha', 'Beta', 'GAMMA']

    Sequence membership is straightforward.

    >>> "Hello World" in [s]
    True
    >>> s in ["Hello World"]
    True

    You may test for set inclusion, but candidate and elements
    must both be folded.

    >>> FoldedCase("Hello World") in {s}
    True
    >>> s in {FoldedCase("Hello World")}
    True

    String inclusion works as long as the FoldedCase object
    is on the right.

    >>> "hello" in FoldedCase("Hello World")
    True

    But not if the FoldedCase object is on the left:

    >>> FoldedCase('hello') in 'Hello World'
    False

    In that case, use in_:

    >>> FoldedCase('hello').in_('Hello World')
    True

    >>> FoldedCase('hello') > FoldedCase('Hello')
    False
    """

    def __lt__(self, other: str) -> bool:
        return self.lower() < other.lower()

    def __gt__(self, other: str) -> bool:
        return self.lower() > other.lower()

    def __eq__(self, other: object) -> bool:
        return isinstance(other, str) and self.lower() == other.lower()

    def __ne__(self, other: object) -> bool:
        return isinstance(other, str) and self.lower() != other.lower()

    def __hash__(self) -> int:
        return hash(self.lower())

    def __contains__(self, other: object) -> bool:
        return isinstance(other, str) and super().lower().__contains__(other.lower())

    def in_(self, other: str) -> bool:
        "Does self appear in other?"
        return self in FoldedCase(other)

    # cache lower since it's likely to be called frequently.
    @method_cache
    def lower(self) -> str:
        return super().lower()

    def index(
        self,
        sub: str,
        start: Optional[SupportsIndex] = None,
        end: Optional[SupportsIndex] = None,
    ) -> int:
        return self.lower().index(sub.lower(), start, end)

    def split(self, splitter: Optional[str] = None, maxsplit: int = 0) -> List[str]:
        if splitter is None:
            return super().split()
        pattern = re.compile(re.escape(splitter), re.I)
        return pattern.split(self, maxsplit)
