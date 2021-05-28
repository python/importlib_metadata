import sys


collect_ignore = [
    # this module fails mypy tests because 'setup.py' matches './setup.py'
    'prepare/example/setup.py',
]


def pytest_configure():
    remove_importlib_metadata()


def remove_importlib_metadata():
    """
    Because pytest imports importlib_metadata, the coverage
    reports are broken (#322). So work around the issue by
    undoing the changes made by pytest's import of
    importlib_metadata (if any).
    """
    if sys.meta_path[-1].__class__.__name__ == 'MetadataPathFinder':
        del sys.meta_path[-1]
    for mod in list(sys.modules):
        if mod.startswith('importlib_metadata'):
            del sys.modules[mod]
