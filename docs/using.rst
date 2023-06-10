.. _using:

=================================
 Using :mod:`!importlib_metadata`
=================================

``importlib_metadata`` is a library that provides access to
the metadata of an installed :term:`packaging:Distribution Package`,
such as its entry points
or its top-level names (:term:`packaging:Import Package`\s, modules, if any).
Built in part on Python's import system, this library
intends to replace similar functionality in the `entry point
API`_ and `metadata API`_ of ``pkg_resources``.  Along with
:mod:`importlib.resources`,
this package can eliminate the need to use the older and less efficient
``pkg_resources`` package.

``importlib_metadata`` operates on third-party *distribution packages*
installed into Python's ``site-packages`` directory via tools such as
`pip <https://pypi.org/project/pip/>`_.
Specifically, it works with distributions with discoverable
``dist-info`` or ``egg-info`` directories,
and metadata defined by the :ref:`packaging:core-metadata`.

.. important::

   These are *not* necessarily equivalent to or correspond 1:1 with
   the top-level *import package* names
   that can be imported inside Python code.
   One *distribution package* can contain multiple *import packages*
   (and single modules),
   and one top-level *import package*
   may map to multiple *distribution packages*
   if it is a namespace package.
   You can use :ref:`package_distributions() <package-distributions>`
   to get a mapping between them.

By default, distribution metadata can live on the file system
or in zip archives on
:data:`sys.path`.  Through an extension mechanism, the metadata can live almost
anywhere.


.. seealso::

   https://importlib-metadata.readthedocs.io/
      The documentation for ``importlib_metadata``, which supplies a
      backport of ``importlib.metadata``.
      This includes an `API reference
      <https://importlib-metadata.readthedocs.io/en/latest/api.html>`__
      for this module's classes and functions,
      as well as a `migration guide
      <https://importlib-metadata.readthedocs.io/en/latest/migration.html>`__
      for existing users of ``pkg_resources``.


Overview
========

Let's say you wanted to get the version string for a
:term:`packaging:Distribution Package` you've installed
using ``pip``.  We start by creating a virtual environment and installing
something into it::

    $ python -m venv example
    $ source example/bin/activate
    (example) $ python -m pip install importlib_metadata
    (example) $ python -m pip install wheel

You can get the version string for ``wheel`` by running the following::

    (example) $ python
    >>> from importlib_metadata import version
    >>> version('wheel')
    '0.32.3'

You can also get a collection of entry points selectable by properties of the EntryPoint (typically 'group' or 'name'), such as
``console_scripts``, ``distutils.commands`` and others.  Each group contains a
collection of :ref:`EntryPoint <entry-points>` objects.

You can get the :ref:`metadata for a distribution <metadata>`::

    >>> list(metadata('wheel'))
    ['Metadata-Version', 'Name', 'Version', 'Summary', 'Home-page', 'Author', 'Author-email', 'Maintainer', 'Maintainer-email', 'License', 'Project-URL', 'Project-URL', 'Project-URL', 'Keywords', 'Platform', 'Classifier', 'Classifier', 'Classifier', 'Classifier', 'Classifier', 'Classifier', 'Classifier', 'Classifier', 'Classifier', 'Classifier', 'Classifier', 'Classifier', 'Requires-Python', 'Provides-Extra', 'Requires-Dist', 'Requires-Dist']

You can also get a :ref:`distribution's version number <version>`, list its
:ref:`constituent files <files>`, and get a list of the distribution's
:ref:`requirements`.


Functional API
==============

This package provides the following functionality via its public API.


.. _entry-points:

Entry points
------------

The ``entry_points()`` function returns a collection of entry points.
Entry points are represented by ``EntryPoint`` instances;
each ``EntryPoint`` has a ``.name``, ``.group``, and ``.value`` attributes and
a ``.load()`` method to resolve the value.  There are also ``.module``,
``.attr``, and ``.extras`` attributes for getting the components of the
``.value`` attribute.

Query all entry points::

    >>> eps = entry_points()

The ``entry_points()`` function returns an ``EntryPoints`` object,
a collection of all ``EntryPoint`` objects with ``names`` and ``groups``
attributes for convenience::

    >>> sorted(eps.groups)
    ['console_scripts', 'distutils.commands', 'distutils.setup_keywords', 'egg_info.writers', 'setuptools.installation']

``EntryPoints`` has a ``select`` method to select entry points
matching specific properties. Select entry points in the
``console_scripts`` group::

    >>> scripts = eps.select(group='console_scripts')

Equivalently, since ``entry_points`` passes keyword arguments
through to select::

    >>> scripts = entry_points(group='console_scripts')

Pick out a specific script named "wheel" (found in the wheel project)::

    >>> 'wheel' in scripts.names
    True
    >>> wheel = scripts['wheel']

Equivalently, query for that entry point during selection::

    >>> (wheel,) = entry_points(group='console_scripts', name='wheel')
    >>> (wheel,) = entry_points().select(group='console_scripts', name='wheel')

Inspect the resolved entry point::

    >>> wheel
    EntryPoint(name='wheel', value='wheel.cli:main', group='console_scripts')
    >>> wheel.module
    'wheel.cli'
    >>> wheel.attr
    'main'
    >>> wheel.extras
    []
    >>> main = wheel.load()
    >>> main
    <function main at 0x103528488>

The ``group`` and ``name`` are arbitrary values defined by the package author
and usually a client will wish to resolve all entry points for a particular
group.  Read `the setuptools docs
<https://setuptools.pypa.io/en/latest/userguide/entry_point.html>`_
for more information on entry points, their definition, and usage.

*Compatibility Note*

The "selectable" entry points were introduced in ``importlib_metadata``
3.6 and Python 3.10. Prior to those changes, ``entry_points`` accepted
no parameters and always returned a dictionary of entry points, keyed
by group. With ``importlib_metadata`` 5.0 and Python 3.12,
``entry_points`` always returns an ``EntryPoints`` object. See
`backports.entry_points_selectable <https://pypi.org/project/backports.entry_points_selectable>`_
for compatibility options.


.. _metadata:

Distribution metadata
---------------------

Every :term:`packaging:Distribution Package` includes some metadata,
which you can extract using the
``metadata()`` function::

    >>> wheel_metadata = metadata('wheel')

The keys of the returned data structure, a ``PackageMetadata``,
name the metadata keywords, and
the values are returned unparsed from the distribution metadata::

    >>> wheel_metadata['Requires-Python']
    '>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*'

``PackageMetadata`` also presents a ``json`` attribute that returns
all the metadata in a JSON-compatible form per PEP 566::

    >>> wheel_metadata.json['requires_python']
    '>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*'

.. note::

    The actual type of the object returned by ``metadata()`` is an
    implementation detail and should be accessed only through the interface
    described by the
    `PackageMetadata protocol <https://importlib-metadata.readthedocs.io/en/latest/api.html#importlib_metadata.PackageMetadata>`_.


.. _version:

Distribution versions
---------------------

The ``version()`` function is the quickest way to get a
:term:`packaging:Distribution Package`'s version
number, as a string::

    >>> version('wheel')
    '0.32.3'


.. _files:

Distribution files
------------------

You can also get the full set of files contained within a distribution.  The
``files()`` function takes a :term:`packaging:Distribution Package` name
and returns all of the
files installed by this distribution.  Each file object returned is a
``PackagePath``, a :class:`pathlib.PurePath` derived object with additional ``dist``,
``size``, and ``hash`` properties as indicated by the metadata.  For example::

    >>> util = [p for p in files('wheel') if 'util.py' in str(p)][0]
    >>> util
    PackagePath('wheel/util.py')
    >>> util.size
    859
    >>> util.dist
    <importlib_metadata._hooks.PathDistribution object at 0x101e0cef0>
    >>> util.hash
    <FileHash mode: sha256 value: bYkw5oMccfazVCoYQwKkkemoVyMAFoR34mmKBx8R1NI>

Once you have the file, you can also read its contents::

    >>> print(util.read_text())
    import base64
    import sys
    ...
    def as_bytes(s):
        if isinstance(s, text_type):
            return s.encode('utf-8')
        return s

You can also use the ``locate`` method to get a the absolute path to the
file::

    >>> util.locate()  # doctest: +SKIP
    PosixPath('/home/gustav/example/lib/site-packages/wheel/util.py')

In the case where the metadata file listing files
(RECORD or SOURCES.txt) is missing, ``files()`` will
return ``None``. The caller may wish to wrap calls to
``files()`` in `always_iterable
<https://more-itertools.readthedocs.io/en/stable/api.html#more_itertools.always_iterable>`_
or otherwise guard against this condition if the target
distribution is not known to have the metadata present.

.. _requirements:

Distribution requirements
-------------------------

To get the full set of requirements for a :term:`packaging:Distribution Package`,
use the ``requires()``
function::

    >>> requires('wheel')
    ["pytest (>=3.0.0) ; extra == 'test'", "pytest-cov ; extra == 'test'"]


.. _package-distributions:
.. _import-distribution-package-mapping:

Mapping import to distribution packages
---------------------------------------

A convenience method to resolve the :term:`packaging:Distribution Package`
name (or names, in the case of a namespace package)
that provide each importable top-level
Python module or :term:`packaging:Import Package`::

    >>> packages_distributions()
    {'importlib_metadata': ['importlib-metadata'], 'yaml': ['PyYAML'], 'jaraco': ['jaraco.classes', 'jaraco.functools'], ...}

Some editable installs, `do not supply top-level names
<https://github.com/pypa/packaging-problems/issues/609>`_, and thus this
function is not reliable with such installs.

.. _distributions:

Distributions
=============

While the above API is the most common and convenient usage, you can get all
of that information from the ``Distribution`` class.  A ``Distribution`` is an
abstract object that represents the metadata for
a Python :term:`packaging:Distribution Package`.  You can
get the ``Distribution`` instance::

    >>> from importlib_metadata import distribution
    >>> dist = distribution('wheel')

Thus, an alternative way to get the version number is through the
``Distribution`` instance::

    >>> dist.version
    '0.32.3'

There are all kinds of additional metadata available on the ``Distribution``
instance::

    >>> dist.metadata['Requires-Python']
    '>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*'
    >>> dist.metadata['License']
    'MIT'

The full set of available metadata is not described here.
See the :ref:`packaging:core-metadata` for additional details.


Distribution Discovery
======================

By default, this package provides built-in support for discovery of metadata
for file system and zip file :term:`packaging:Distribution Package`\s.
This metadata finder search defaults to ``sys.path``, but varies slightly in how it interprets those values from how other import machinery does. In particular:

- ``importlib_metadata`` does not honor :class:`bytes` objects on ``sys.path``.
- ``importlib_metadata`` will incidentally honor :py:class:`pathlib.Path` objects on ``sys.path`` even though such values will be ignored for imports.


Extending the search algorithm
==============================

Because :term:`packaging:Distribution Package` metadata
is not available through :data:`sys.path` searches, or
package loaders directly,
the metadata for a distribution is found through import
system :ref:`finders <finders-and-loaders>`.  To find a distribution package's metadata,
``importlib.metadata`` queries the list of :term:`meta path finders <meta path finder>` on
:data:`sys.meta_path`.

By default ``importlib_metadata`` installs a finder for distribution packages
found on the file system.
This finder doesn't actually find any *distributions*,
but it can find their metadata.

The abstract class :py:class:`importlib.abc.MetaPathFinder` defines the
interface expected of finders by Python's import system.
``importlib_metadata`` extends this protocol by looking for an optional
``find_distributions`` callable on the finders from
:data:`sys.meta_path` and presents this extended interface as the
``DistributionFinder`` abstract base class, which defines this abstract
method::

    @abc.abstractmethod
    def find_distributions(context=DistributionFinder.Context()):
        """Return an iterable of all Distribution instances capable of
        loading the metadata for packages for the indicated ``context``.
        """

The ``DistributionFinder.Context`` object provides ``.path`` and ``.name``
properties indicating the path to search and name to match and may
supply other relevant context.

What this means in practice is that to support finding distribution package
metadata in locations other than the file system, subclass
``Distribution`` and implement the abstract methods. Then from
a custom finder, return instances of this derived ``Distribution`` in the
``find_distributions()`` method.


.. _`entry point API`: https://setuptools.readthedocs.io/en/latest/pkg_resources.html#entry-points
.. _`metadata API`: https://setuptools.readthedocs.io/en/latest/pkg_resources.html#metadata-api
