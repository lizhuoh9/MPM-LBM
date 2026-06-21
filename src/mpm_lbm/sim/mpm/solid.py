"""Canonical MPM solid surface. Legacy implementation: ``src.mpm_solid``."""

from ..._legacy import legacy_getattr

_LEGACY_MODULE = "src.mpm_solid"
__all__ = ("MPMSolid3D",)


def __getattr__(name):
    return legacy_getattr(_LEGACY_MODULE, __all__, name)
