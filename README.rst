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

:func:`metadata` takes a distribution package name and returns
the metadata for that package (as :class:`email.Message`).

:func:`version` takes a distribution package name and returns the
version for that package.

:func:`entry_points` takes a distribution package name and returns
a structure of entry points declared by that package.

:func:`resolve` accepts an entry point as returned by
:func:`entry_points` and resolves it to the module or callable that
it references.

:func:`read_text` takes the distribution package name and a filename
in that package's info directory and return the text of that file.

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
- Packages installed as eggs.

Eggs
----

Not only does ``importlib_metadata`` not support loading metadata
from eggs, it will crash when it attempts to load metadata for
any package that's an egg.

``easy_install`` creates eggs when installing packages, which is why
you should use ``pip`` to install packages. ``pip`` never installs
eggs. There are some cases, however, where a project's usage
may not be able to avoid ``easy_install``. In particular, if a project
uses ``setup.py test``, any ``install_requires`` of that project that
aren't already installed will be installed using ``easy_install``.
Additionally, any project defining ``setup_requires`` may get those
dependencies installed as eggs if those dependencies aren't met before
setup.py is invoked (for any command).

Because ``importlib_metadata`` doesn't support loading metadata from
eggs and because ``importlib_metadata`` calls itself to get its own version,
simply importing ``importlib_metadata`` will fail if it is installed as an
egg. Any package that incorporates ``importlib_metadata`` (directly
or indirectly) should be prepared to guide its users to tools that avoid
installing eggs (such as `pip <https://pypi.org/project/pip>`_ and
`tox <https://pypi.org/project/tox>`_).

More detail and discussion can be found at
`issue 19 <https://gitlab.com/python-devs/importlib_metadata/issues/19>`_.


Project details
===============

 * Project home: https://gitlab.com/python-devs/importlib_metadata
 * Report bugs at: https://gitlab.com/python-devs/importlib_metadata/issues
 * Code hosting: https://gitlab.com/python-devs/importlib_metadata.git
 * Documentation: http://importlib_metadata.readthedocs.io/
