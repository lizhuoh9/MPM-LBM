"""Canonical LBM fluid surface. Legacy implementation: ``src.lbm_fluid``."""

from ..._legacy import legacy_getattr

_LEGACY_MODULE = "src.lbm_fluid"
__all__ = ("LBMFluid3D",)


def __getattr__(name):
    return legacy_getattr(_LEGACY_MODULE, __all__, name)
