"""Canonical moving-boundary surface. Legacy implementation: ``src.moving_boundary_coupling``."""

from ..._legacy import legacy_getattr

_LEGACY_MODULE = "src.moving_boundary_coupling"
__all__ = ("MovingBoundaryFSICoupler3D",)


def __getattr__(name):
    return legacy_getattr(_LEGACY_MODULE, __all__, name)
