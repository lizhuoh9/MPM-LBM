"""Canonical FSI driver surface."""

from ..._legacy import legacy_getattr

_LEGACY_MODULE = "src.fsi_driver"
__all__ = ("FSIDriver3D",)


def __getattr__(name):
    return legacy_getattr(_LEGACY_MODULE, __all__, name)
