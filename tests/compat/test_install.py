"""
The finder installed on ``sys.meta_path`` is particular to the backport;
the stdlib reaches ``MetadataPathFinder`` through its own ``PathFinder``
and so never publishes a finder of its own (#525).
"""

import contextlib
import importlib.util
import os
import sys
import unittest
from unittest import mock

from importlib_metadata import _compat


class FinderInstallTests(unittest.TestCase):
    def test_installed_after_module_initialized(self):
        """
        Install the finder only after the module can satisfy it.

        An installed finder resolves ``PathDistribution`` from the module
        globals, so a finder installed before the module body completes is
        one that anything walking ``sys.meta_path`` would trip over.
        """
        snapshots = []

        def capture(cls):
            snapshots.append(set(sys._getframe(1).f_globals))
            return cls

        spec = importlib.util.find_spec('importlib_metadata')
        with contextlib.ExitStack() as stack:
            stack.enter_context(mock.patch.object(_compat, 'install', capture))
            # Don't let the re-executed module leak a fork handler.
            stack.enter_context(mock.patch.object(os, 'register_at_fork', create=True))
            spec.loader.exec_module(importlib.util.module_from_spec(spec))

        (globals_at_install,) = snapshots
        assert 'PathDistribution' in globals_at_install
