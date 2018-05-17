# This is a hack until setuptools supports reading a version out of a file
# without importing.  Once that bug is fix-released, you can remove this file
# and update the setup.cfg file.
#
# https://github.com/pypa/setuptools/issues/1358

# Yes, it's horrible to let reference counting reclaim the open file object,
# but oh well, this will exit soon.
__version__ = open('importlib_metadata/version.txt').read().strip()
