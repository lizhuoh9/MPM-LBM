"""Canonical LBM config surface. Legacy implementation: ``src.lbm_config``."""

from ..._legacy import legacy_getattr

_LEGACY_MODULE = "src.lbm_config"
__all__ = ("LBMConfig",)


def __getattr__(name):
    return legacy_getattr(_LEGACY_MODULE, __all__, name)
