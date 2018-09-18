=========================
 ``importlib_metadata``
=========================

``importlib_metadata`` is a library to access the metadata for a Python
package.  It is intended to be ported to Python 3.8.


Usage
=====

``importlib_metadata``, unlike its sister packages importlib and
importlib.resources, operates on Python Distribution packages (the
package as installed by pip or similar).

This module exposes a few functions:

:func:`version` takes a distribution package name and returns the
version for that package.

:func:`entry_points` takes a distribution package name and returns
a structure of entry points declared by that package.

:func:`resolve` accepts an entry point as returned by
:func:`entry_points` and resolves it to the module or callable that
it references.

Support for Custom Package Installers
=====================================

``importlib_metadata`` provides hooks for third-party package installers
through their declared finders. A custom installer, if it provides its
own finder for installed packages, should also provide on that finder
a ``find_distribution`` callable that when called with
the name of a package will return a ``Distribution`` instance capable
of loading the metadata for that named package (or None if that finder
has no knowledge of that package or its metadata).


Caveats
=======

This project primarily supports third-party packages installed by PyPA
tools (or other conforming packages). It does not support:

- Packages in the stdlib.
- Packages installed without metadata.


Project details
===============

 * Project home: https://gitlab.com/python-devs/importlib_metadata
 * Report bugs at: https://gitlab.com/python-devs/importlib_metadata/issues
 * Code hosting: https://gitlab.com/python-devs/importlib_metadata.git
 * Documentation: http://importlib_metadata.readthedocs.io/
