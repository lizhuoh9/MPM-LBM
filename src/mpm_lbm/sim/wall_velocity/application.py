"""Canonical bridge surface. Implementation remains legacy until Step 59."""

from ..._legacy import legacy_getattr

_LEGACY_MODULE = "src.wall_velocity_application"
__all__ = ("apply_wall_velocity_application_to_lbm",)
BRIDGE_IS_TEMPORARY_UNTIL_STEP59 = True


def __getattr__(name):
    return legacy_getattr(_LEGACY_MODULE, __all__, name)
