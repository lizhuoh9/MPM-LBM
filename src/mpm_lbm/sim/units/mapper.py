"""Canonical grid/unit mapper surface."""

from ..._legacy import legacy_getattr

_LEGACY_MODULE = "src.units"
__all__ = ("GridUnitMapper",)


def __getattr__(name):
    return legacy_getattr(_LEGACY_MODULE, __all__, name)
