import typing
import pathlib

from importlib_metadata import _meta


class TestSimplePath:
    def test_cast_from_Path(self):
        _: _meta.SimplePath = typing.cast(pathlib.Path, None)
