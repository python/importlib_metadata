=========================
 ``importlib_metadata``
=========================

``importlib_metadata`` is a library to access the metadata for a Python
package.  It is intended to be ported to Python 3.8.


Usage
=====

See the `online documentation <https://importlib_metadata.readthedocs.io/>`_
for usage details.

`Finder authors
<https://docs.python.org/3/reference/import.html#finders-and-loaders>`_ can
also add support for custom package installers.  See the above documentation
for details.


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
