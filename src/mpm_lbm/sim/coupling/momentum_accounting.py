"""Canonical momentum-accounting surface."""

from ..._legacy import legacy_getattr

_LEGACY_MODULE = "src.momentum_accounting"
__all__ = ("MomentumAccounting3D",)


def __getattr__(name):
    return legacy_getattr(_LEGACY_MODULE, __all__, name)
