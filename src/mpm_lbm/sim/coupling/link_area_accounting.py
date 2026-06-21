"""Canonical link-area accounting surface."""

from ..._legacy import legacy_getattr

_LEGACY_MODULE = "src.link_area_accounting"
__all__ = ("LinkAreaMomentumAccounting3D",)


def __getattr__(name):
    return legacy_getattr(_LEGACY_MODULE, __all__, name)
