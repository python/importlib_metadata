=========================
 importlib_metadata NEWS
=========================

0.9
===
* Fixed issue where entry points without an attribute would raise an
  Exception.  Closes #40.
* Removed unused ``name`` parameter from ``entry_points()``. Closes #44.
* ``DistributionFinder`` classes must now be instantiated before
  being placed on ``sys.meta_path``.

0.8
===
* This library can now discover/enumerate all installed packages. **This
  backward-incompatible change alters the protocol finders must
  implement to support distribution package discovery.** Closes #24.
* The signature of ``find_distributions()`` on custom installer finders
  should now accept two parameters, ``name`` and ``path`` and
  these parameters must supply defaults.
* The ``entry_points()`` method no longer accepts a package name
  but instead returns all entry points in a dictionary keyed by the
  ``EntryPoint.group``. The ``resolve`` method has been removed. Instead,
  call ``EntryPoint.load()``, which has the same semantics as
  ``pkg_resources`` and ``entrypoints``.  **This is a backward incompatible
  change.**
* Metadata is now always returned as Unicode text regardless of
  Python version. Closes #29.
* This library can now discover metadata for a 'local' package (found
  in the current-working directory). Closes #27.
* Added ``files()`` function for resolving files from a distribution.
* Added a new ``requires()`` function, which returns the requirements
  for a package suitable for parsing by
  ``packaging.requirements.Requirement``. Closes #18.
* The top-level ``read_text()`` function has been removed.  Use
  ``PackagePath.read_text()`` on instances returned by the ``files()``
  function.  **This is a backward incompatible change.**
* Release dates are now automatically injected into the changelog
  based on SCM tags.

0.7
===
* Fixed issue where packages with dashes in their names would
  not be discovered. Closes #21.
* Distribution lookup is now case-insensitive. Closes #20.
* Wheel distributions can no longer be discovered by their module
  name. Like Path distributions, they must be indicated by their
  distribution package name.

0.6
===
* Removed ``importlib_metadata.distribution`` function. Now
  the public interface is primarily the utility functions exposed
  in ``importlib_metadata.__all__``. Closes #14.
* Added two new utility functions ``read_text`` and
  ``metadata``.

0.5
===
* Updated README and removed details about Distribution
  class, now considered private. Closes #15.
* Added test suite support for Python 3.4+.
* Fixed SyntaxErrors on Python 3.4 and 3.5. !12
* Fixed errors on Windows joining Path elements. !15

0.4
===
* Housekeeping.

0.3
===
* Added usage documentation.  Closes #8
* Add support for getting metadata from wheels on ``sys.path``.  Closes #9

0.2
===
* Added ``importlib_metadata.entry_points()``.  Closes #1
* Added ``importlib_metadata.resolve()``.  Closes #12
* Add support for Python 2.7.  Closes #4

0.1
===
* Initial release.


..
   Local Variables:
   mode: change-log-mode
   indent-tabs-mode: nil
   sentence-end-double-space: t
   fill-column: 78
   coding: utf-8
   End:
