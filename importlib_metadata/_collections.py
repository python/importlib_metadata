import collections


class freezable_defaultdict(collections.defaultdict):
    """
    Mix-in to freeze a defaultdict.

    >>> dd = freezable_defaultdict(list)
    >>> dd[0].append('1')
    >>> dd.freeze()
    >>> dd[1]
    []
    >>> len(dd)
    1
    """

    def __missing__(self, key):
        return getattr(self, '_frozen', super().__missing__)(key)

    def freeze(self):
        self._frozen = lambda key: self.default_factory()
