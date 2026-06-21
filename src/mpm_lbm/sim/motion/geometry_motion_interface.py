"""Canonical bridge surface. Implementation remains legacy until Step 59."""

from ..._legacy import legacy_getattr

_LEGACY_MODULE = "src.geometry_motion_interface"
__all__ = ("write_geometry_motion_interface_report",)
BRIDGE_IS_TEMPORARY_UNTIL_STEP59 = True


def __getattr__(name):
    return legacy_getattr(_LEGACY_MODULE, __all__, name)
