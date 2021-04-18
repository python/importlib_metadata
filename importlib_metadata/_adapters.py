import re
import textwrap
import email.message

from ._functools import method_cache


class Message(email.message.Message):
    def __new__(cls, orig: email.message.Message):
        res = super().__new__(cls)
        vars(res).update(vars(orig))
        return res

    def __init__(self, *args, **kwargs):
        self._headers = self._repair_headers()

    # suppress spurious error from mypy
    def __iter__(self):
        return super().__iter__()

    def _repair_headers(self):
        def redent(value):
            "Correct for RFC822 indentation"
            if not value or '\n' not in value:
                return value
            return textwrap.dedent(' ' * 8 + value)

        headers = [(key, redent(value)) for key, value in vars(self)['_headers']]
        if self._payload:
            headers.append(('Description', self.get_payload()))
        return headers

    @property
    def json(self):
        """
        Convert PackageMetadata to a JSON-compatible format
        per PEP 0566.
        """
        multiple_use = set(
            map(
                FoldedCase,
                [
                    'Classifier',
                    'Obsoletes-Dist',
                    'Platform',
                    'Project-URL',
                    'Provides-Dist',
                    'Provides-Extra',
                    'Requires-Dist',
                    'Requires-External',
                    'Supported-Platform',
                ],
            )
        )

        def transform(key):
            value = self.get_all(key) if key in multiple_use else self[key]
            if key == 'Keywords':
                value = re.split(r'\s+', value)
            tk = key.lower().replace('-', '_')
            return tk, value

        return dict(map(transform, map(FoldedCase, self)))


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

    def __lt__(self, other):
        return self.lower() < other.lower()

    def __gt__(self, other):
        return self.lower() > other.lower()

    def __eq__(self, other):
        return self.lower() == other.lower()

    def __ne__(self, other):
        return self.lower() != other.lower()

    def __hash__(self):
        return hash(self.lower())

    def __contains__(self, other):
        return super(FoldedCase, self).lower().__contains__(other.lower())

    def in_(self, other):
        "Does self appear in other?"
        return self in FoldedCase(other)

    # cache lower since it's likely to be called frequently.
    @method_cache
    def lower(self):
        return super(FoldedCase, self).lower()

    def index(self, sub):
        return self.lower().index(sub.lower())

    def split(self, splitter=' ', maxsplit=0):
        pattern = re.compile(re.escape(splitter), re.I)
        return pattern.split(self, maxsplit)
