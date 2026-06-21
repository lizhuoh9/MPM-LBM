"""Canonical projection surface. Legacy implementation: ``src.projection``."""

from ..._legacy import legacy_getattr

_LEGACY_MODULE = "src.projection"
__all__ = ("MPMToLBMProjector3D",)


def __getattr__(name):
    return legacy_getattr(_LEGACY_MODULE, __all__, name)
