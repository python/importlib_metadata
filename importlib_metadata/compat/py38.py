import os
import pathlib
import sys
import types


def wrap(path):
    """
    Workaround for https://github.com/python/cpython/issues/67271 where ".."
    isn't added by pathlib.Path.relative_to() when path is not
    a subpath of root.
    One example of such a package is dask-labextension, which uses
    jupyter-packaging to install JupyterLab javascript files outside
    of site-packages.
    """

    def relative_to(root, *, walk_up=False):
        return pathlib.Path(os.path.relpath(path, root))

    return types.SimpleNamespace(relative_to=relative_to)


relative_fix = wrap if sys.version_info < (3, 9) else lambda x: x
