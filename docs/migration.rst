.. _migration:

=================
 Migration guide
=================

The following guide will help you migrate common ``pkg_resources``
APIs to ``importlib_metadata``. ``importlib_metadata`` aims to
replace the following ``pkg_resources`` APIs:

* ``pkg_resources.iter_entry_points()``
* ``pkg_resources.require()``
* convenience functions
* ``pkg_resources.find_distributions()``
* ``pkg_resources.get_distribution()``

Other functionality from ``pkg_resources`` is replaced by other
packages such as
`importlib_resources <https://pypi.org/project/importlib_resources>`_
and `packaging <https://pypi.org/project/packaging>`_.


pkg_resources.iter_entry_points()
=================================

``importlib_metadata`` provides :ref:`entry-points`.

Compatibility note: entry points provided by importlib_metadata
do not have the following implicit behaviors found in those
from ``pkg_resources``:

- Each EntryPoint is not automatically validated to match. To
  ensure each one is validated, invoke any property on the
  object (e.g. ``ep.name``).

- When invoking ``EntryPoint.load()``, no checks are performed
  to ensure the declared extras are installed. If this behavior
  is desired/required, it is left to the user to perform the
  check and install any dependencies. See
  `importlib_metadata#368 <https://github.com/python/importlib_metadata/issues/368>`_
  for more details.

pkg_resources.require()
=======================

``importlib_metadata`` does not provide support for dynamically
discovering or requiring distributions nor does it provide any
support for managing the "working set". Furthermore,
``importlib_metadata`` assumes that only one version of a given
distribution is discoverable at any time (no support for multi-version
installs). Any projects that require the above behavior needs to
provide that behavior independently.

``importlib_metadata`` does aim to resolve metadata concerns late
such that any dynamic changes to package availability should be
reflected immediately.

Convenience functions
=====================

In addition to the support for direct access to ``Distribution``
objects (below), ``importlib_metadata`` presents some top-level
functions for easy access to the most common metadata:

- :ref:`metadata` queries the metadata fields from the distribution.
- :ref:`version` provides quick access to the distribution version.
- :ref:`requirements` presents the requirements of the distribution.
- :ref:`files` provides file-like access to the data blobs backing
  the metadata.

pkg_resources.find_distributions()
==================================

``importlib_metadata`` provides functionality
similar to ``find_distributions()``. Both ``distributions(...)`` and
``Distribution.discover(...)`` return an iterable of :ref:`distributions`
matching the indicated parameters.

pkg_resources.get_distribution()
=================================

Similar to ``distributions``, the ``distribution()`` function provides
access to a single distribution by name.

