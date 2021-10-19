Welcome to |project| documentation!
===================================

``importlib_metadata`` is a library which provides an API for accessing an
installed package's metadata (see :pep:`566`), such as its entry points or its top-level
name.  This functionality intends to replace most uses of ``pkg_resources``
`entry point API`_ and `metadata API`_.  Along with :mod:`importlib.resources`
and newer (backported as :doc:`importlib_resources <importlib_resources:index>`),
this package can eliminate the need to use the older and less
efficient ``pkg_resources`` package.

``importlib_metadata`` supplies a backport of
:doc:`importlib.metadata <library/importlib.metadata>`,
enabling early access to features of future Python versions and making
functionality available for older Python versions. Users are encouraged to
use the Python standard library where suitable and fall back to
this library for future compatibility. Developers looking for detailed API
descriptions should refer to the standard library documentation.

The documentation here includes a general :ref:`usage <using>` guide.


.. toctree::
   :maxdepth: 1

   using
   api
   history


Project details
===============

 * Project home: https://github.com/python/importlib_metadata
 * Report bugs at: https://github.com/python/importlib_metadata/issues
 * Code hosting: https://github.com/python/importlib_metadata
 * Documentation: https://importlib_metadata.readthedocs.io/


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


.. _`entry point API`: https://setuptools.readthedocs.io/en/latest/pkg_resources.html#entry-points
.. _`metadata API`: https://setuptools.readthedocs.io/en/latest/pkg_resources.html#metadata-api
