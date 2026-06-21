"""Canonical FSI driver config surface."""

from ..._legacy import legacy_getattr

_LEGACY_MODULE = "src.fsi_config"
__all__ = ("FSIDriverConfig",)


def __getattr__(name):
    return legacy_getattr(_LEGACY_MODULE, __all__, name)
