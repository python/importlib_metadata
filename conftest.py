import sys

collect_ignore = [
    # this module fails mypy tests because 'setup.py' matches './setup.py'
    'tests/data/sources/example/setup.py',
]


def pytest_configure():
    remove_importlib_metadata()


def remove_importlib_metadata():
    """
    Ensure importlib_metadata is not imported yet.

    Because pytest or other modules might import
    importlib_metadata, the coverage reports are broken (#322).
    Work around the issue by undoing the changes made by a
    previous import of importlib_metadata (if any).
    """
    sys.meta_path[:] = [
        item
        for item in sys.meta_path
        if item.__class__.__name__ != 'MetadataPathFinder'
    ]
    for mod in list(sys.modules):
        if mod.startswith('importlib_metadata'):
            del sys.modules[mod]
