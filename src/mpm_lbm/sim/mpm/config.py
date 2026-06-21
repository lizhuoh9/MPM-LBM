"""Canonical MPM config surface. Legacy implementation: ``src.mpm_config``."""

from ..._legacy import legacy_getattr

_LEGACY_MODULE = "src.mpm_config"
__all__ = ("MPMConfig",)


def __getattr__(name):
    return legacy_getattr(_LEGACY_MODULE, __all__, name)
