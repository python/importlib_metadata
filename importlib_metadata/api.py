import io
import re
import abc
import sys
import email
import operator
import functools
import itertools
import collections

from importlib import import_module

if sys.version_info > (3,):  # pragma: nocover
    from configparser import ConfigParser
else:  # pragma: nocover
    from backports.configparser import ConfigParser

try:
    BaseClass = ModuleNotFoundError
except NameError:                                 # pragma: nocover
    BaseClass = ImportError                       # type: ignore


__metaclass__ = type


class PackageNotFoundError(BaseClass):
    """The package was not found."""


class EntryPoint(collections.namedtuple('EntryPointBase', 'name value group')):
    """An entry point as defined by Python packaging conventions."""

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

    def load(self):
        """Load the entry point from its definition. If only a module
        is indicated by the value, return that module. Otherwise,
        return the named object.
        """
        match = self.pattern.match(self.value)
        module = import_module(match.group('module'))
        attrs = filter(None, match.group('attr').split('.'))
        return functools.reduce(getattr, attrs, module)

    @property
    def extras(self):
        match = self.pattern.match(self.value)
        return list(re.finditer(r'\w+', match.group('extras') or ''))

    @classmethod
    def _from_config(cls, config):
        return [
            cls(name, value, group)
            for group in config.sections()
            for name, value in config.items(group)
            ]

    @classmethod
    def _from_text(cls, text):
        config = ConfigParser()
        try:
            config.read_string(text)
        except AttributeError:  # pragma: nocover
            # Python 2 has no read_string
            config.readfp(io.StringIO(text))
        return EntryPoint._from_config(config)

    def __iter__(self):
        """
        Supply iter so one may construct dicts of EntryPoints easily.
        """
        return iter((self.name, self))


class Distribution:
    """A Python distribution package."""

    @abc.abstractmethod
    def read_text(self, filename):
        """Attempt to load metadata file given by the name.

        :param filename: The name of the file in the distribution info.
        :return: The text if found, otherwise None.
        """

    @classmethod
    def from_name(cls, name):
        """Return the Distribution for the given package name.

        :param name: The name of the distribution package to search for.
        :return: The Distribution instance (or subclass thereof) for the named
            package, if found.
        :raises PackageNotFoundError: When the named package's distribution
            metadata cannot be found.
        """
        for resolver in cls._discover_resolvers():
            dists = resolver(name)
            dist = next(dists, None)
            if dist is not None:
                return dist
        else:
            raise PackageNotFoundError(name)

    @classmethod
    def discover(cls):
        """Return an iterable of Distribution objects for all packages.

        :return: Iterable of Distribution objects for all packages.
        """
        return itertools.chain.from_iterable(
            resolver()
            for resolver in cls._discover_resolvers()
            )

    @staticmethod
    def _discover_resolvers():
        """Search the meta_path for resolvers."""
        declared = (
            getattr(finder, 'find_distributions', None)
            for finder in sys.meta_path
            )
        return filter(None, declared)

    @property
    def metadata(self):
        """Return the parsed metadata for this Distribution.

        The returned object will have keys that name the various bits of
        metadata.  See PEP 566 for details.
        """
        text = self.read_text('METADATA') or self.read_text('PKG-INFO')
        return _email_message_from_string(text)

    @property
    def version(self):
        """Return the 'Version' metadata for the distribution package."""
        return self.metadata['Version']

    @property
    def entry_points(self):
        return EntryPoint._from_text(self.read_text('entry_points.txt'))

    @property
    def requires(self):
        return self._read_dist_info_reqs() or self._read_egg_info_reqs()

    def _read_dist_info_reqs(self):
        spec = self.metadata['Requires-Dist']
        return spec and filter(None, spec.splitlines())

    def _read_egg_info_reqs(self):
        source = self.read_text('requires.txt')
        return self._deps_from_requires_text(source)

    @classmethod
    def _deps_from_requires_text(cls, source):
        section_pairs = cls._read_sections(source.splitlines())
        sections = {
            section: list(map(operator.itemgetter('line'), results))
            for section, results in
            itertools.groupby(section_pairs, operator.itemgetter('section'))
            }
        return cls._convert_egg_info_reqs_to_simple_reqs(sections)

    @staticmethod
    def _read_sections(lines):
        section = None
        for line in filter(None, lines):
            section_match = re.match(r'\[(.*)\]$', line)
            if section_match:
                section = section_match.group(1)
                continue
            yield locals()

    @staticmethod
    def _convert_egg_info_reqs_to_simple_reqs(sections):
        """
        Historically, setuptools would solicit and store 'extra'
        requirements, including those with environment markers,
        in separate sections. More modern tools expect each
        dependency to be defined separately, with any relevant
        extras and environment markers attached directly to that
        requirement. This method converts the former to the
        latter. See _test_deps_from_requires_text for an example.
        """
        def make_condition(name):
            return name and 'extra == "{name}"'.format(name=name)

        def parse_condition(section):
            section = section or ''
            extra, sep, markers = section.partition(':')
            if extra and markers:
                markers = '({markers})'.format(markers=markers)
            conditions = list(filter(None, [markers, make_condition(extra)]))
            return '; ' + ' and '.join(conditions) if conditions else ''

        for section, deps in sections.items():
            for dep in deps:
                yield dep + parse_condition(section)


def _email_message_from_string(text):
    # Work around https://bugs.python.org/issue25545 where
    # email.message_from_string cannot handle Unicode on Python 2.
    if sys.version_info < (3,):                     # nocoverpy3
        io_buffer = io.StringIO(text)
        return email.message_from_file(io_buffer)
    return email.message_from_string(text)          # nocoverpy2


def distribution(package):
    """Get the ``Distribution`` instance for the given package.

    :param package: The name of the package as a string.
    :return: A ``Distribution`` instance (or subclass thereof).
    """
    return Distribution.from_name(package)


def distributions():
    """Get all ``Distribution`` instances in the current environment.

    :return: An iterable of ``Distribution`` instances.
    """
    return Distribution.discover()


def metadata(package):
    """Get the metadata for the package.

    :param package: The name of the distribution package to query.
    :return: An email.Message containing the parsed metadata.
    """
    return Distribution.from_name(package).metadata


def version(package):
    """Get the version string for the named package.

    :param package: The name of the distribution package to query.
    :return: The version string for the package as defined in the package's
        "Version" metadata key.
    """
    return distribution(package).version


def entry_points(name=None):
    """Return EntryPoint objects for all installed packages.

    :return: EntryPoint objects for all installed packages.
    """
    eps = itertools.chain.from_iterable(
        dist.entry_points for dist in distributions())
    by_group = operator.attrgetter('group')
    ordered = sorted(eps, key=by_group)
    grouped = itertools.groupby(ordered, by_group)
    return {
        group: tuple(eps)
        for group, eps in grouped
        }


def read_text(package, filename):
    """
    Read the text of the file in the distribution info directory.
    """
    return distribution(package).read_text(filename)


def requires(package):
    """
    Return a list of requirements for the indicated distribution.

    :return: An iterator of requirements, suitable for
    packaging.requirement.Requirement.
    """
    return distribution(package).requires
