import string
import textwrap
import itertools

from . import _meta


class JSONMeta(_meta.PackageMetadata):
    def __init__(self, orig: _meta.PackageMetadata):
        self.orig = orig

    def __getitem__(self, item):
        return self.orig.__getitem__(item)

    def __len__(self):
        return self.orig.__len__()  # pragma: nocover

    def __contains__(self, item):
        return self.orig.__contains__(item)  # pragma: nocover

    def __iter__(self):
        return self.orig.__iter__()

    def get_all(self, name):
        return self.orig.get_all(name)

    def get_payload(self):
        return self.orig.get_payload()

    @property
    def json(self):
        """
        Convert PackageMetadata to a JSON-compatible format
        per PEP 0566.
        """
        # TODO: Need to match case-insensitive
        multiple_use = {
            'Classifier',
            'Obsoletes-Dist',
            'Platform',
            'Project-URL',
            'Provides-Dist',
            'Provides-Extra',
            'Requires-Dist',
            'Requires-External',
            'Supported-Platform',
        }

        def redent(value):
            "Correct for RFC822 indentation"
            if not value or '\n' not in value:
                return value
            return textwrap.dedent(' ' * 8 + value)

        def transform(key):
            value = self.get_all(key) if key in multiple_use else redent(self[key])
            if key == 'Keywords':
                value = value.split(string.whitespace)
            if not value and key == 'Description':
                value = self.get_payload()
            tk = key.lower().replace('-', '_')
            return tk, value

        desc = ['Description'] if self.get_payload() else []
        keys = itertools.chain(self, desc)
        return dict(map(transform, keys))
