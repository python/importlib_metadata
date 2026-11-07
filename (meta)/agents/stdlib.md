This project shares its codebase with the CPython standard library, where it appears as `importlib.metadata`. The two trees are kept byte-identical: changes made here are synced downstream into CPython, and changes made in CPython are ported back here.

Before changing anything under `importlib_metadata/`, read the [development methodology](https://github.com/python/importlib_metadata/wiki/Development-Methodology) in its entirety. It governs how the two codebases are kept in sync, which files are excluded from the stdlib, and how to verify the trees agree.
