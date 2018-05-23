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

The main feature is the :class:`Distribution` class.

Construct one by passing a top-level module (or package) to
:meth:`Distribution.from_module`:

    >>> dist = importlib_resources.Distribution.from_module(importlib_resources)

From there, the package metadata is available on ``dist.metadata``:

	>>> 'Version' in dist.metadata
	True

The package also provides an interface to load the metadata for
a known distribution package name with :meth:`Distribution.from_name`:

    >>> dist = importlib_resources.Distribution.from_name('importlib_resources')


Distribution Name
=================

This project introduces the concept of a mapping from an imported module
to its distribution package name. Many times, the name of the imported
module or package matches the distribution package (e.g. requests).

Other times, the imported name and distribution package name differ.
For example, the ``path`` module is the top-level module in the
`path.py <https://pypi.org/project/path.py>`_ distribution package
and in the `setuptools <https://pypi.org/project/setuptools>`_
project, there are two top-level packages, ``setuptools`` and
``pkg_resources``, both sharing the same metadata.

For projects where the name of the top level module does not match
exactly to the distribution package name, those modules should present
a ``__dist_name__`` member with the distribution package name
and this property will be used by importlib_metadata to resolve the
metadata for those Python packages.


Caveats
=======

This project primarily supports third-party packages installed by PyPA
tools (or other conforming packages). It does not support:

- Packages in the stdlib.
- Packages installed without metadata.
- Zip packages.
- Packages loaded with custom loaders.

Project details
===============

 * Project home: https://gitlab.com/python-devs/importlib_metadata
 * Report bugs at: https://gitlab.com/python-devs/importlib_metadata/issues
 * Code hosting: https://gitlab.com/python-devs/importlib_metadata.git
 * Documentation: http://importlib_metadata.readthedocs.io/
