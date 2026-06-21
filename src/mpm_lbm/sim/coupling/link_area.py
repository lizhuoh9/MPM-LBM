"""Canonical link-area coupling surface. Legacy implementation: ``src.link_area_coupling``."""

from ..._legacy import legacy_getattr

_LEGACY_MODULE = "src.link_area_coupling"
__all__ = ("LinkAreaMovingBoundaryCoupler3D",)


def __getattr__(name):
    return legacy_getattr(_LEGACY_MODULE, __all__, name)
