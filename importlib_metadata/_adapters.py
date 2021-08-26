import re
import textwrap
import email.message

from ._text import FoldedCase
from typing import Dict, Iterator, List, Tuple, Union


class Message(email.message.Message):
    multiple_use_keys = set(
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
                'Dynamic',
            ],
        )
    )
    """
    Keys that may be indicated multiple times per PEP 566.
    """

    def __new__(cls, orig: email.message.Message) -> 'Message':
        res: Message = super().__new__(cls)
        vars(res).update(vars(orig))
        return res

    def __init__(self, orig: email.message.Message) -> None:
        self._headers = self._repair_headers()

    # suppress spurious error from mypy
    # https://github.com/python/typeshed/pull/5960
    def __iter__(self) -> Iterator[str]:
        return super().__iter__()  # type: ignore[misc,no-any-return]

    def _repair_headers(self) -> List[Tuple[str, str]]:
        def redent(value: str) -> str:
            "Correct for RFC822 indentation"
            if not value or '\n' not in value:
                return value
            return textwrap.dedent(' ' * 8 + value)

        headers = [(key, redent(value)) for key, value in vars(self)['_headers']]
        if self._payload:  # type: ignore[attr-defined]
            headers.append(('Description', self.get_payload()))
        return headers

    @property
    def json(self) -> Dict[str, Union[str, List[str]]]:
        """
        Convert PackageMetadata to a JSON-compatible format
        per PEP 0566.
        """

        def transform(key: FoldedCase) -> Tuple[str, Union[str, List[str]]]:
            value = self.get_all(key) if key in self.multiple_use_keys else self[key]
            if key == 'Keywords':
                value = re.split(r'\s+', value)
            tk = key.lower().replace('-', '_')
            return tk, value

        return dict(map(transform, map(FoldedCase, self)))
