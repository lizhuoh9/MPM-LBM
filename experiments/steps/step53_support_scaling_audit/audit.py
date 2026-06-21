"""Canonical Step 53 support-scaling audit surface."""

from src.mpm_lbm._legacy import legacy_getattr

_LEGACY_MODULE = "src.runtime_geometry_wall_velocity_support_scaling_audit"
__all__ = ("step52_regression_rows",)


def __getattr__(name):
    return legacy_getattr(_LEGACY_MODULE, __all__, name)
