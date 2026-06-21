"""Canonical penalty-coupling surface. Legacy implementation: ``src.coupling``."""

from ..._legacy import legacy_getattr

_LEGACY_MODULE = "src.coupling"
__all__ = ("PenaltyFSICoupler3D",)


def __getattr__(name):
    return legacy_getattr(_LEGACY_MODULE, __all__, name)
