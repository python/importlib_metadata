import collections


class Pair(collections.namedtuple('Pair', 'name value')):
    @classmethod
    def parse(cls, text):
        return cls(*map(str.strip, text.split("=", 1)))
