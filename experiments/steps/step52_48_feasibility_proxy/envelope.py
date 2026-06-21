"""Canonical Step 52 48-grid feasibility proxy envelope surface."""

from src.mpm_lbm._legacy import legacy_getattr

_LEGACY_MODULE = "src.runtime_geometry_wall_velocity_48_feasibility_envelope"
__all__ = ("run_48_feasibility_matrix", "summarize_48_feasibility_matrix", "write_48_feasibility_rows")


def __getattr__(name):
    return legacy_getattr(_LEGACY_MODULE, __all__, name)
