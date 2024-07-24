"""
Compatibility layer with stdlib.
Only needed when distributing via PyPI/3rd-party package.
"""

import sys
from typing import TYPE_CHECKING, List, Union

if TYPE_CHECKING:
    # Avoid circular imports

    from importlib import metadata as _legacy

    from typing_extensions import TypeAlias

    from .. import Distribution, PackagePath, _meta

    if sys.version_info >= (3, 10):
        from importlib.metadata import PackageMetadata as _legacy_Metadata
    else:
        from email.message import Message as _legacy_Metadata

    _PackageMetadataOrLegacy: TypeAlias = Union[_legacy_Metadata, _meta.PackageMetadata]
    _DistributionOrLegacy: TypeAlias = Union[_legacy.Distribution, Distribution]
    _List_PackagePathOrLegacy: TypeAlias = Union[
        List[_legacy.PackagePath], List[PackagePath]
    ]
