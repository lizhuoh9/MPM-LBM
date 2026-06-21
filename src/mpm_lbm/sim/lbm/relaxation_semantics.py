"""Canonical LBM relaxation-semantics surface."""

from ..._legacy import legacy_getattr

_LEGACY_MODULE = "src.lbm_relaxation_semantics"
__all__ = (
    "tau_from_legacy_external_solver_parameter",
    "tau_from_lattice_kinematic_viscosity",
    "relaxation_semantics_summary",
)


def __getattr__(name):
    return legacy_getattr(_LEGACY_MODULE, __all__, name)
