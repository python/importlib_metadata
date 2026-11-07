.. _caveats:

=========
 Caveats
=========

``importlib_metadata`` and :mod:`importlib.metadata` define separate class
hierarchies. This package supplies its own ``Distribution``, ``PackagePath``,
and metadata classes, and neither set derives from the other. Both libraries
discover distributions by querying the finders on :data:`sys.meta_path`, so one
custom provider serves consumers of both and has no say in which of the two a
given consumer uses.

Both libraries present the same protocols, ``IDistribution``, ``IPackagePath``,
and ``PackageMetadata``, and the classes of both satisfy them. Those protocols,
rather than any concrete class, are the interface to write against.

For consumers
=============

A consumer calling ``distributions()`` expects this package's objects, but a
custom provider may supply objects from :mod:`importlib.metadata`. This package
settles most of that on the consumer's behalf, substituting its own class for
each object it recognizes, such as a ``PathDistribution``, a ``PackagePath``,
or an :class:`email.message.Message`. It has no way to reconstruct an arbitrary
``Distribution`` subclass from a custom provider, so it passes such an object
through unchanged.

Annotate against the protocols, then, and do not test an object with
:func:`isinstance` against a concrete class.

.. _caveats-custom-providers:

For custom providers
====================

A provider's objects reach consumers of both libraries, so supply objects that
satisfy ``IDistribution`` whole, not in part. Deriving from ``Distribution``
achieves this: the base class builds the rest of the interface on
``read_text`` and ``locate_file``. Where a class omits a member the protocol
requires, this package emits a :exc:`UserWarning` naming what is missing; a
provider satisfying the protocol whole draws no warning.

Deriving from whichever of the two libraries happens to be importable is not a
general answer. A provider cannot know whether a consumer will import this
package, and importing it to find out activates it in environments that would
otherwise never have used it.

.. versionchanged:: 10.0.0
   Objects a provider supplies from :mod:`importlib.metadata` are adapted to
   this package's classes where they can be, and the warning reports the
   members a class omits rather than firing for any class derived from
   :mod:`importlib.metadata`.
