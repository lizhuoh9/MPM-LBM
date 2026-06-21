"""Canonical unified simulation config surface."""

from ..._legacy import legacy_getattr

_LEGACY_MODULE = "src.sim_config"
__all__ = ("UnifiedSimConfig",)


def __getattr__(name):
    return legacy_getattr(_LEGACY_MODULE, __all__, name)
