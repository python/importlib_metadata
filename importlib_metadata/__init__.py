import os
import re
import abc
import csv
import sys
import zipp
import email
import pathlib
import operator
import textwrap
import warnings
import functools
import itertools
import posixpath
import collections

from . import _adapters, _meta
from ._collections import FreezableDefaultDict, Pair
from ._compat import (
    NullFinder,
    Protocol,
    PyPy_repr,
    SupportsIndex,
    install,
    pypy_partial,
)
from ._functools import method_cache
from ._itertools import unique_everseen
from ._meta import PackageMetadata, SimplePath

from contextlib import suppress
from importlib import import_module
from importlib.abc import MetaPathFinder
from itertools import starmap
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    Iterator,
    KeysView,
    List,
    Mapping,
    Match,
    NamedTuple,
    Optional,
    Set,
    Tuple,
    Type,
    TypeVar,
    Union,
    ValuesView,
    overload,
)


__all__ = [
    'Distribution',
    'DistributionFinder',
    'PackageMetadata',
    'PackageNotFoundError',
    'distribution',
    'distributions',
    'entry_points',
    'files',
    'metadata',
    'packages_distributions',
    'requires',
    'version',
]


class PackageNotFoundError(ModuleNotFoundError):
    """The package was not found."""

    args: Tuple[str]

    def __str__(self) -> str:
        return f"No package metadata was found for {self.name}"

    @property
    def name(self) -> str:  # type: ignore[override]
        (name,) = self.args
        return name


class Sectioned:
    """
    A simple entry point config parser for performance

    >>> for item in Sectioned.read(Sectioned._sample):
    ...     print(item)
    Pair(name='sec1', value='# comments ignored')
    Pair(name='sec1', value='a = 1')
    Pair(name='sec1', value='b = 2')
    Pair(name='sec2', value='a = 2')

    >>> res = Sectioned.section_pairs(Sectioned._sample)
    >>> item = next(res)
    >>> item.name
    'sec1'
    >>> item.value
    Pair(name='a', value='1')
    >>> item = next(res)
    >>> item.value
    Pair(name='b', value='2')
    >>> item = next(res)
    >>> item.name
    'sec2'
    >>> item.value
    Pair(name='a', value='2')
    >>> list(res)
    []
    """

    _sample = textwrap.dedent(
        """
        [sec1]
        # comments ignored
        a = 1
        b = 2

        [sec2]
        a = 2
        """
    ).lstrip()

    @classmethod
    def section_pairs(cls, text: str) -> Iterator[Pair]:
        return (
            section._replace(value=Pair.parse(section.value))
            for section in cls.read(text, filter_=cls.valid)
            if section.name is not None
        )

    @staticmethod
    def read(
        text: str, filter_: Optional[Callable[[str], bool]] = None
    ) -> Iterator[Pair]:
        lines = filter(filter_, map(str.strip, text.splitlines()))
        name = None
        for value in lines:
            section_match = value.startswith('[') and value.endswith(']')
            if section_match:
                name = value.strip('[]')
                continue
            yield Pair(name, value)

    @staticmethod
    def valid(line: str) -> bool:
        return line != '' and not line.startswith('#')


class EntryPointBase(NamedTuple):
    name: str
    value: str
    group: str


class EntryPoint(PyPy_repr, EntryPointBase):
    """An entry point as defined by Python packaging conventions.

    See `the packaging docs on entry points
    <https://packaging.python.org/specifications/entry-points/>`_
    for more information.
    """

    pattern = re.compile(
        r'(?P<module>[\w.]+)\s*'
        r'(:\s*(?P<attr>[\w.]+))?\s*'
        r'(?P<extras>\[.*\])?\s*$'
    )
    """
    A regular expression describing the syntax for an entry point,
    which might look like:

        - module
        - package.module
        - package.module:attribute
        - package.module:object.attribute
        - package.module:attr [extra1, extra2]

    Other combinations are possible as well.

    The expression is lenient about whitespace around the ':',
    following the attr, and following any extras.
    """

    dist: 'Distribution'

    def load(self) -> Any:
        """Load the entry point from its definition. If only a module
        is indicated by the value, return that module. Otherwise,
        return the named object.
        """
        match = self.pattern.match(self.value)
        assert match is not None
        module = import_module(match.group('module'))
        attrs = filter(None, (match.group('attr') or '').split('.'))
        return functools.reduce(getattr, attrs, module)

    @property
    def module(self) -> str:
        match = self.pattern.match(self.value)
        assert match is not None
        return match.group('module')

    @property
    def attr(self) -> str:
        match = self.pattern.match(self.value)
        assert match is not None
        return match.group('attr')

    @property
    def extras(self) -> List[Match[str]]:
        match = self.pattern.match(self.value)
        assert match is not None
        return list(re.finditer(r'\w+', match.group('extras') or ''))

    def _for(self, dist: 'Distribution') -> 'EntryPoint':
        self.dist = dist
        return self

    def __iter__(self) -> Iterator[object]:  # type: ignore[override]
        """
        Supply iter so one may construct dicts of EntryPoints by name.
        """
        msg = (
            "Construction of dict of EntryPoints is deprecated in "
            "favor of EntryPoints."
        )
        warnings.warn(msg, DeprecationWarning)
        return iter((self.name, self))

    def __reduce__(self) -> Tuple[Type['EntryPoint'], Tuple[str, str, str]]:
        return (
            self.__class__,
            (self.name, self.value, self.group),
        )

    def matches(self, **params: str) -> bool:
        attrs = (getattr(self, param) for param in params)
        return all(map(operator.eq, params.values(), attrs))


class _SupportsLessThan(Protocol):
    def __lt__(self, __other: Any) -> bool:
        ...  # pragma: no cover


_T = TypeVar('_T')
_DeprecatedListT = TypeVar('_DeprecatedListT', bound='DeprecatedList[Any]')
_SupportsLessThanT = TypeVar('_SupportsLessThanT', bound=_SupportsLessThan)


class DeprecatedList(List[_T]):
    """
    Allow an otherwise immutable object to implement mutability
    for compatibility.

    >>> recwarn = getfixture('recwarn')
    >>> dl = DeprecatedList(range(3))
    >>> dl[0] = 1
    >>> dl.append(3)
    >>> del dl[3]
    >>> dl.reverse()
    >>> dl.sort()
    >>> dl.extend([4])
    >>> dl.pop(-1)
    4
    >>> dl.remove(1)
    >>> dl += [5]
    >>> dl + [6]
    [1, 2, 5, 6]
    >>> dl + (6,)
    [1, 2, 5, 6]
    >>> dl.insert(0, 0)
    >>> dl
    [0, 1, 2, 5]
    >>> dl == [0, 1, 2, 5]
    True
    >>> dl == (0, 1, 2, 5)
    True
    >>> len(recwarn)
    1
    """

    _warn = functools.partial(
        warnings.warn,
        "EntryPoints list interface is deprecated. Cast to list if needed.",
        DeprecationWarning,
        stacklevel=pypy_partial(2),
    )

    @overload
    def __setitem__(self, index: SupportsIndex, value: _T) -> None:
        ...  # pragma: no cover

    @overload
    def __setitem__(self, index: slice, value: Iterable[_T]) -> None:
        ...  # pragma: no cover

    def __setitem__(self, index: Union[SupportsIndex, slice], value: Any) -> None:
        self._warn()
        super().__setitem__(index, value)

    def __delitem__(self, index: Union[SupportsIndex, slice]) -> None:
        self._warn()
        super().__delitem__(index)

    def append(self, value: _T) -> None:
        self._warn()
        super().append(value)

    def reverse(self) -> None:
        self._warn()
        super().reverse()

    def extend(self, values: Iterable[_T]) -> None:
        self._warn()
        super().extend(values)

    def pop(self, index: int = -1) -> _T:
        self._warn()
        return super().pop(index)

    def remove(self, value: _T) -> None:
        self._warn()
        super().remove(value)

    def __iadd__(self: _DeprecatedListT, values: Iterable[_T]) -> _DeprecatedListT:
        self._warn()
        return super().__iadd__(values)

    def __add__(
        self: _DeprecatedListT, other: Union[List[_T], Tuple[_T, ...]]
    ) -> _DeprecatedListT:
        if not isinstance(other, tuple):
            self._warn()
            other = tuple(other)
        return self.__class__(tuple(self) + other)

    def insert(self, index: int, value: _T) -> None:
        self._warn()
        super().insert(index, value)

    @overload
    def sort(
        self: 'DeprecatedList[_SupportsLessThanT]',
        *,
        key: None = ...,
        reverse: bool = ...,
    ) -> None:
        ...  # pragma: no cover

    @overload
    def sort(
        self, *, key: Callable[[_T], _SupportsLessThan], reverse: bool = ...
    ) -> None:
        ...  # pragma: no cover

    def sort(
        self,
        *,
        key: Optional[Callable[[_T], _SupportsLessThan]] = None,
        reverse: bool = False,
    ) -> None:
        self._warn()
        super().sort(key=key, reverse=reverse)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, list):
            self._warn()
            other = tuple(other)

        return tuple(self).__eq__(other)


class EntryPoints(DeprecatedList[EntryPoint]):
    """
    An immutable collection of selectable EntryPoint objects.
    """

    __slots__ = ()

    @overload
    def __getitem__(self, name: SupportsIndex) -> EntryPoint:
        ...  # pragma: no cover

    @overload
    def __getitem__(self, name: slice) -> List[EntryPoint]:
        ...  # pragma: no cover

    @overload
    def __getitem__(self, name: str) -> EntryPoint:
        ...  # pragma: no cover

    def __getitem__(
        self, name: Union[SupportsIndex, slice, str]
    ) -> Union[EntryPoint, List[EntryPoint]]:
        """
        Get the EntryPoint in self matching name.
        """
        if isinstance(name, (SupportsIndex, slice)):
            warnings.warn(
                "Accessing entry points by index is deprecated. "
                "Cast to tuple if needed.",
                DeprecationWarning,
                stacklevel=2,
            )
            return super().__getitem__(name)
        try:
            return next(iter(self.select(name=name)))
        except StopIteration:
            raise KeyError(name)

    def select(self, **params: str) -> 'EntryPoints':
        """
        Select entry points from self that match the
        given parameters (typically group and/or name).
        """
        return EntryPoints(ep for ep in self if ep.matches(**params))

    @property
    def names(self) -> Set[str]:
        """
        Return the set of all names of all entry points.
        """
        return {ep.name for ep in self}

    @property
    def groups(self) -> Set[str]:
        """
        Return the set of all groups of all entry points.

        For coverage while SelectableGroups is present.
        >>> EntryPoints().groups
        set()
        """
        return {ep.group for ep in self}

    @classmethod
    def _from_text_for(cls, text: str, dist: 'Distribution') -> 'EntryPoints':
        return cls(ep._for(dist) for ep in cls._from_text(text))

    @classmethod
    def _from_text(cls, text: str) -> Iterator['EntryPoint']:
        return itertools.starmap(EntryPoint, cls._parse_groups(text or ''))

    @staticmethod
    def _parse_groups(text: str) -> Iterator[Tuple[str, str, Optional[str]]]:
        return (
            (item.value.name, item.value.value, item.name)
            for item in Sectioned.section_pairs(text)
        )


_K = TypeVar('_K')
_V = TypeVar('_V')


class DeprecatedDict(Dict[_K, _V]):
    """
    Compatibility add-in for mapping to indicate that
    mapping behavior is deprecated.

    >>> recwarn = getfixture('recwarn')
    >>> dd = DeprecatedDict(foo='bar')
    >>> dd.get('baz', None)
    >>> dd['foo']
    'bar'
    >>> list(dd)
    ['foo']
    >>> list(dd.keys())
    ['foo']
    >>> 'foo' in dd
    True
    >>> list(dd.values())
    ['bar']
    >>> len(recwarn)
    1
    """

    _warn = functools.partial(
        warnings.warn,
        "SelectableGroups dict interface is deprecated. Use select.",
        DeprecationWarning,
        stacklevel=pypy_partial(2),
    )

    def __getitem__(self, name: _K) -> _V:
        self._warn()
        return super().__getitem__(name)

    @overload
    def get(self, name: _K) -> Optional[_V]:
        ...  # pragma: no cover

    @overload
    def get(self, name: _K, default: _T) -> Union[_V, _T]:
        ...  # pragma: no cover

    def get(self, name: _K, default: Optional[_T] = None) -> Union[_V, _T, None]:
        self._warn()
        return super().get(name, default)

    def __iter__(self) -> Iterator[_K]:
        self._warn()
        return super().__iter__()

    def __contains__(self, value: object) -> bool:
        self._warn()
        return super().__contains__(value)

    def keys(self) -> KeysView[_K]:
        self._warn()
        return super().keys()

    def values(self) -> ValuesView[_V]:
        self._warn()
        return super().values()


class SelectableGroups(DeprecatedDict[str, EntryPoints]):
    """
    A backward- and forward-compatible result from
    entry_points that fully implements the dict interface.
    """

    @classmethod
    def load(cls, eps: Iterable[EntryPoint]) -> 'SelectableGroups':
        by_group = operator.attrgetter('group')
        ordered = sorted(eps, key=by_group)
        grouped = itertools.groupby(ordered, by_group)
        return cls((group, EntryPoints(eps)) for group, eps in grouped)

    @property
    def _all(self) -> EntryPoints:
        """
        Reconstruct a list of all entrypoints from the groups.
        """
        groups = super(DeprecatedDict, self).values()
        return EntryPoints(itertools.chain.from_iterable(groups))

    @property
    def groups(self) -> Set[str]:
        return self._all.groups

    @property
    def names(self) -> Set[str]:
        """
        for coverage:
        >>> SelectableGroups().names
        set()
        """
        return self._all.names

    @overload
    def select(self) -> 'SelectableGroups':
        ...  # pragma: no cover

    @overload
    def select(self, *, name: str, **params: str) -> EntryPoints:
        ...  # pragma: no cover

    @overload
    def select(self, *, value: str, **params: str) -> EntryPoints:
        ...  # pragma: no cover

    @overload
    def select(self, *, group: str, **params: str) -> EntryPoints:
        ...  # pragma: no cover

    @overload
    def select(self, *, module: str, **params: str) -> EntryPoints:
        ...  # pragma: no cover

    @overload
    def select(self, *, attr: str, **params: str) -> EntryPoints:
        ...  # pragma: no cover

    def select(self, **params: str) -> Union['SelectableGroups', EntryPoints]:
        if not params:
            return self
        return self._all.select(**params)


class PackagePath(pathlib.PurePosixPath):
    """A reference to a path in a package"""

    hash: Optional['FileHash']
    size: Optional[int]
    dist: 'Distribution'

    def read_text(self, encoding: str = 'utf-8') -> str:
        return self.locate().read_text(encoding=encoding)

    def read_binary(self) -> bytes:
        return self.locate().read_bytes()

    def locate(self) -> SimplePath:
        """Return a path-like object for this path"""
        return self.dist.locate_file(self)


class FileHash:
    def __init__(self, spec: str) -> None:
        self.mode, _, self.value = spec.partition('=')

    def __repr__(self) -> str:
        return f'<FileHash mode: {self.mode} value: {self.value}>'


class Distribution:
    """A Python distribution package."""

    @abc.abstractmethod
    def read_text(self, filename: Union[str, 'os.PathLike[str]']) -> Optional[str]:
        """Attempt to load metadata file given by the name.

        :param filename: The name of the file in the distribution info.
        :return: The text if found, otherwise None.
        """

    @abc.abstractmethod
    def locate_file(self, path: Union[str, 'os.PathLike[str]']) -> SimplePath:
        """
        Given a path to a file in this distribution, return a path
        to it.
        """

    @classmethod
    def from_name(cls, name: str) -> 'Distribution':
        """Return the Distribution for the given package name.

        :param name: The name of the distribution package to search for.
        :return: The Distribution instance (or subclass thereof) for the named
            package, if found.
        :raises PackageNotFoundError: When the named package's distribution
            metadata cannot be found.
        """
        for resolver in cls._discover_resolvers():
            dists = resolver(DistributionFinder.Context(name=name))
            dist = next(iter(dists), None)
            if dist is not None:
                return dist
        else:
            raise PackageNotFoundError(name)

    @classmethod
    def discover(cls, **kwargs: Any) -> Iterator['PathDistribution']:
        """Return an iterable of Distribution objects for all packages.

        Pass a ``context`` or pass keyword arguments for constructing
        a context.

        :context: A ``DistributionFinder.Context`` object.
        :return: Iterable of Distribution objects for all packages.
        """
        context: Optional[DistributionFinder.Context] = kwargs.pop('context', None)
        if context and kwargs:
            raise ValueError("cannot accept context and kwargs")
        context = context or DistributionFinder.Context(**kwargs)
        return itertools.chain.from_iterable(
            resolver(context) for resolver in cls._discover_resolvers()
        )

    @staticmethod
    def at(path: Union[str, 'os.PathLike[str]']) -> 'PathDistribution':
        """Return a Distribution for the indicated metadata path

        :param path: a string or path-like object
        :return: a concrete Distribution instance for the path
        """
        return PathDistribution(pathlib.Path(path))

    @staticmethod
    def _discover_resolvers() -> Iterator[
        Callable[['DistributionFinder.Context'], Iterator['PathDistribution']]
    ]:
        """Search the meta_path for resolvers."""
        declared = (
            getattr(finder, 'find_distributions', None) for finder in sys.meta_path
        )
        return filter(None, declared)

    @classmethod
    def _local(cls, root: str = '.') -> 'PathDistribution':
        from pep517 import build, meta

        system = build.compat_system(root)
        builder = functools.partial(
            meta.build,
            source_dir=root,
            system=system,
        )
        return PathDistribution(zipp.Path(meta.build_as_zip(builder)))

    @property
    def metadata(self) -> _meta.PackageMetadata:
        """Return the parsed metadata for this Distribution.

        The returned object will have keys that name the various bits of
        metadata.  See PEP 566 for details.
        """
        text = (
            self.read_text('METADATA')
            or self.read_text('PKG-INFO')
            # This last clause is here to support old egg-info files.  Its
            # effect is to just end up using the PathDistribution's self._path
            # (which points to the egg-info file) attribute unchanged.
            or self.read_text('')
            or ''
        )
        return _adapters.Message(email.message_from_string(text))

    @property
    def name(self) -> str:
        """Return the 'Name' metadata for the distribution package."""
        return self.metadata['Name']

    @property
    def _normalized_name(self) -> str:
        """Return a normalized version of the name."""
        return Prepared.normalize(self.name)

    @property
    def version(self) -> str:
        """Return the 'Version' metadata for the distribution package."""
        return self.metadata['Version']

    @property
    def entry_points(self) -> EntryPoints:
        return EntryPoints._from_text_for(
            self.read_text('entry_points.txt') or '', self
        )

    @property
    def files(self) -> Optional[List[PackagePath]]:
        """Files in this distribution.

        :return: List of PackagePath for this distribution or None

        Result is `None` if the metadata file that enumerates files
        (i.e. RECORD for dist-info or SOURCES.txt for egg-info) is
        missing.
        Result may be empty if the metadata exists but is empty.
        """
        file_lines = self._read_files_distinfo() or self._read_files_egginfo()

        def make_file(
            name: str, hash: Optional[str] = None, size_str: Optional[str] = None
        ) -> PackagePath:
            result = PackagePath(name)
            result.hash = FileHash(hash) if hash else None
            result.size = int(size_str) if size_str else None
            result.dist = self
            return result

        return (
            None
            if file_lines is None
            else list(starmap(make_file, csv.reader(file_lines)))
        )

    def _read_files_distinfo(self) -> Optional[Iterable[str]]:
        """
        Read the lines of RECORD
        """
        text = self.read_text('RECORD')
        return text and text.splitlines()

    def _read_files_egginfo(self) -> Optional[Iterable[str]]:
        """
        SOURCES.txt might contain literal commas, so wrap each line
        in quotes.
        """
        text = self.read_text('SOURCES.txt')
        return text and map('"{}"'.format, text.splitlines())

    @property
    def requires(self) -> Optional[List[str]]:
        """Generated requirements specified for this Distribution"""
        reqs = self._read_dist_info_reqs() or self._read_egg_info_reqs()
        return None if reqs is None else list(reqs)

    def _read_dist_info_reqs(self) -> List[str]:
        return self.metadata.get_all('Requires-Dist')

    def _read_egg_info_reqs(self) -> Optional[Iterable[str]]:
        source = self.read_text('requires.txt')
        return source and self._deps_from_requires_text(source)

    @classmethod
    def _deps_from_requires_text(cls, source: str) -> Iterator[str]:
        return cls._convert_egg_info_reqs_to_simple_reqs(Sectioned.read(source))

    @staticmethod
    def _convert_egg_info_reqs_to_simple_reqs(
        sections: Iterator[Pair],
    ) -> Iterator[str]:
        """
        Historically, setuptools would solicit and store 'extra'
        requirements, including those with environment markers,
        in separate sections. More modern tools expect each
        dependency to be defined separately, with any relevant
        extras and environment markers attached directly to that
        requirement. This method converts the former to the
        latter. See _test_deps_from_requires_text for an example.
        """

        def make_condition(name: str) -> str:
            return name and f'extra == "{name}"'

        def parse_condition(section: Optional[str]) -> str:
            section = section or ''
            extra, sep, markers = section.partition(':')
            if extra and markers:
                markers = f'({markers})'
            conditions = list(filter(None, [markers, make_condition(extra)]))
            return '; ' + ' and '.join(conditions) if conditions else ''

        for section in sections:
            yield section.value + parse_condition(section.name)


class DistributionFinder(MetaPathFinder):
    """
    A MetaPathFinder capable of discovering installed distributions.
    """

    class Context:
        """
        Keyword arguments presented by the caller to
        ``distributions()`` or ``Distribution.discover()``
        to narrow the scope of a search for distributions
        in all DistributionFinders.

        Each DistributionFinder may expect any parameters
        and should attempt to honor the canonical
        parameters defined below when appropriate.
        """

        name: Optional[str] = None
        """
        Specific name for which a distribution finder should match.
        A name of ``None`` matches all distributions.
        """

        def __init__(self, **kwargs: object) -> None:
            vars(self).update(kwargs)

        @property
        def path(self) -> str:
            """
            The sequence of directory path that a distribution finder
            should search.

            Typically refers to Python installed package paths such as
            "site-packages" directories and defaults to ``sys.path``.
            """
            return vars(self).get('path', sys.path)

    @abc.abstractmethod
    def find_distributions(
        self, context: Context = Context()
    ) -> Iterable['PathDistribution']:
        """
        Find distributions.

        Return an iterable of all Distribution instances capable of
        loading the metadata for packages matching the ``context``,
        a DistributionFinder.Context instance.
        """


class FastPath:
    """
    Micro-optimized class for searching a path for
    children.
    """

    @functools.lru_cache()  # type: ignore[misc]
    def __new__(cls, root: Union[str, 'os.PathLike[str]']) -> 'FastPath':
        return super().__new__(cls)  # type: ignore[no-any-return]

    def __init__(self, root: Union[str, 'os.PathLike[str]']) -> None:
        self.root = str(root)

    def joinpath(self, child: Union[str, 'os.PathLike[str]']) -> pathlib.Path:
        return pathlib.Path(self.root, child)

    def children(self) -> Iterable[str]:
        with suppress(Exception):
            return os.listdir(self.root or '')
        with suppress(Exception):
            return self.zip_children()
        return []

    def zip_children(self) -> Dict[str, None]:
        zip_path = zipp.Path(self.root)
        names = zip_path.root.namelist()
        self.joinpath = zip_path.joinpath  # type: ignore[assignment]

        return dict.fromkeys(child.split(posixpath.sep, 1)[0] for child in names)

    def search(self, name: 'Prepared') -> Iterator[pathlib.Path]:
        return self.lookup(self.mtime).search(name)

    @property
    def mtime(self) -> Optional[float]:
        with suppress(OSError):
            return os.stat(self.root).st_mtime
        self.lookup.cache_clear()  # type: ignore[attr-defined]
        return None

    @method_cache
    def lookup(self, mtime: Optional[float]) -> 'Lookup':
        return Lookup(self)


class Lookup:
    def __init__(self, path: FastPath) -> None:
        base = os.path.basename(path.root).lower()
        base_is_egg = base.endswith(".egg")
        self.infos = FreezableDefaultDict[Optional[str], List[pathlib.Path]](list)
        self.eggs = FreezableDefaultDict[Optional[str], List[pathlib.Path]](list)

        for child in path.children():
            low = child.lower()
            if low.endswith((".dist-info", ".egg-info")):
                # rpartition is faster than splitext and suitable for this purpose.
                name = low.rpartition(".")[0].partition("-")[0]
                normalized = Prepared.normalize(name)
                self.infos[normalized].append(path.joinpath(child))
            elif base_is_egg and low == "egg-info":
                name = base.rpartition(".")[0].partition("-")[0]
                legacy_normalized = Prepared.legacy_normalize(name)
                self.eggs[legacy_normalized].append(path.joinpath(child))

        self.infos.freeze()
        self.eggs.freeze()

    def search(self, prepared: 'Prepared') -> Iterator[pathlib.Path]:
        infos = (
            self.infos[prepared.normalized]
            if prepared
            else itertools.chain.from_iterable(self.infos.values())
        )
        eggs = (
            self.eggs[prepared.legacy_normalized]
            if prepared
            else itertools.chain.from_iterable(self.eggs.values())
        )
        return itertools.chain(infos, eggs)


class Prepared:
    """
    A prepared search for metadata on a possibly-named package.
    """

    normalized: Optional[str] = None
    legacy_normalized: Optional[str] = None

    def __init__(self, name: Optional[str]) -> None:
        self.name = name
        if name is None:
            return
        self.normalized = self.normalize(name)
        self.legacy_normalized = self.legacy_normalize(name)

    @staticmethod
    def normalize(name: str) -> str:
        """
        PEP 503 normalization plus dashes as underscores.
        """
        return re.sub(r"[-_.]+", "-", name).lower().replace('-', '_')

    @staticmethod
    def legacy_normalize(name: str) -> str:
        """
        Normalize the package name as found in the convention in
        older packaging tools versions and specs.
        """
        return name.lower().replace('-', '_')

    def __bool__(self) -> bool:
        return bool(self.name)


@install
class MetadataPathFinder(NullFinder, DistributionFinder):
    """A degenerate finder for distribution packages on the file system.

    This finder supplies only a find_distributions() method for versions
    of Python that do not have a PathFinder find_distributions().
    """

    def find_distributions(
        self, context: DistributionFinder.Context = DistributionFinder.Context()
    ) -> Iterator['PathDistribution']:
        """
        Find distributions.

        Return an iterable of all Distribution instances capable of
        loading the metadata for packages matching ``context.name``
        (or all names if ``None`` indicated) along the paths in the list
        of directories ``context.path``.
        """
        found = self._search_paths(context.name, context.path)
        return map(PathDistribution, found)

    @classmethod
    def _search_paths(
        cls, name: Optional[str], paths: Iterable[Union[str, 'os.PathLike[str]']]
    ) -> Iterator[pathlib.Path]:
        """Find metadata directories in paths heuristically."""
        prepared = Prepared(name)
        return itertools.chain.from_iterable(
            path.search(prepared) for path in map(FastPath, paths)
        )

    def invalidate_caches(cls) -> None:
        FastPath.__new__.cache_clear()


class PathDistribution(Distribution):
    def __init__(self, path: SimplePath) -> None:
        """Construct a distribution.

        :param path: SimplePath indicating the metadata directory.
        """
        self._path = path

    def read_text(self, filename: Union[str, 'os.PathLike[str]']) -> Optional[str]:
        with suppress(
            FileNotFoundError,
            IsADirectoryError,
            KeyError,
            NotADirectoryError,
            PermissionError,
        ):
            return self._path.joinpath(filename).read_text(encoding='utf-8')
        return None

    read_text.__doc__ = Distribution.read_text.__doc__

    def locate_file(self, path: Union[str, 'os.PathLike[str]']) -> SimplePath:
        return self._path.parent / path

    @property
    def _normalized_name(self) -> str:
        """
        Performance optimization: where possible, resolve the
        normalized name from the file system path.
        """
        stem = os.path.basename(str(self._path))
        return self._name_from_stem(stem) or super()._normalized_name

    def _name_from_stem(self, stem: str) -> Optional[str]:
        name, ext = os.path.splitext(stem)
        if ext not in ('.dist-info', '.egg-info'):
            return None
        name, sep, rest = stem.partition('-')
        return name


def distribution(distribution_name: str) -> Distribution:
    """Get the ``Distribution`` instance for the named package.

    :param distribution_name: The name of the distribution package as a string.
    :return: A ``Distribution`` instance (or subclass thereof).
    """
    return Distribution.from_name(distribution_name)


def distributions(**kwargs: Any) -> Iterator[PathDistribution]:
    """Get all ``Distribution`` instances in the current environment.

    :return: An iterable of ``Distribution`` instances.
    """
    return Distribution.discover(**kwargs)


def metadata(distribution_name: str) -> _meta.PackageMetadata:
    """Get the metadata for the named package.

    :param distribution_name: The name of the distribution package to query.
    :return: A PackageMetadata containing the parsed metadata.
    """
    return Distribution.from_name(distribution_name).metadata


def version(distribution_name: str) -> str:
    """Get the version string for the named package.

    :param distribution_name: The name of the distribution package to query.
    :return: The version string for the package as defined in the package's
        "Version" metadata key.
    """
    return distribution(distribution_name).version


@overload
def entry_points() -> SelectableGroups:
    ...  # pragma: no cover


@overload
def entry_points(*, name: str, **params: str) -> EntryPoints:
    ...  # pragma: no cover


@overload
def entry_points(*, value: str, **params: str) -> EntryPoints:
    ...  # pragma: no cover


@overload
def entry_points(*, group: str, **params: str) -> EntryPoints:
    ...  # pragma: no cover


@overload
def entry_points(*, module: str, **params: str) -> EntryPoints:
    ...  # pragma: no cover


@overload
def entry_points(*, attr: str, **params: str) -> EntryPoints:
    ...  # pragma: no cover


def entry_points(**params: str) -> Union[EntryPoints, SelectableGroups]:
    """Return EntryPoint objects for all installed packages.

    Pass selection parameters (group or name) to filter the
    result to entry points matching those properties (see
    EntryPoints.select()).

    For compatibility, returns ``SelectableGroups`` object unless
    selection parameters are supplied. In the future, this function
    will return ``EntryPoints`` instead of ``SelectableGroups``
    even when no selection parameters are supplied.

    For maximum future compatibility, pass selection parameters
    or invoke ``.select`` with parameters on the result.

    :return: EntryPoints or SelectableGroups for all installed packages.
    """
    norm_name = operator.attrgetter('_normalized_name')
    eps = itertools.chain.from_iterable(
        dist.entry_points for dist in unique_everseen(distributions(), key=norm_name)
    )
    return SelectableGroups.load(eps).select(**params)


def files(distribution_name: str) -> Optional[List[PackagePath]]:
    """Return a list of files for the named package.

    :param distribution_name: The name of the distribution package to query.
    :return: List of files composing the distribution.
    """
    return distribution(distribution_name).files


def requires(distribution_name: str) -> Optional[List[str]]:
    """
    Return a list of requirements for the named package.

    :return: An iterator of requirements, suitable for
        packaging.requirement.Requirement.
    """
    return distribution(distribution_name).requires


def packages_distributions() -> Mapping[str, List[str]]:
    """
    Return a mapping of top-level packages to their
    distributions.

    >>> import collections.abc
    >>> pkgs = packages_distributions()
    >>> all(isinstance(dist, collections.abc.Sequence) for dist in pkgs.values())
    True
    """
    pkg_to_dist = collections.defaultdict(list)
    for dist in distributions():
        for pkg in _top_level_declared(dist) or _top_level_inferred(dist):
            pkg_to_dist[pkg].append(dist.metadata['Name'])
    return dict(pkg_to_dist)


def _top_level_declared(dist: Distribution) -> List[str]:
    return (dist.read_text('top_level.txt') or '').split()


def _top_level_inferred(dist: Distribution) -> Set[str]:
    return {
        f.parts[0] if len(f.parts) > 1 else f.with_suffix('').name
        for f in dist.files or []
        if f.suffix == ".py"
    }
