"""Explicit LBM relaxation-parameter semantics.

The legacy external solver parameter is named separately from standard lattice
kinematic viscosity so reports and tests cannot silently treat the legacy
`niu` field as validated physical viscosity.
"""


LEGACY_EXTERNAL_SOLVER_RELAXATION_PARAMETER = "legacy_external_solver_relaxation_parameter"
STANDARD_LATTICE_KINEMATIC_VISCOSITY = "standard_lattice_kinematic_viscosity"
DEFAULT_TAU_CONVENTION = LEGACY_EXTERNAL_SOLVER_RELAXATION_PARAMETER


def tau_from_legacy_external_solver_parameter(niu: float) -> float:
    return float(niu) / 3.0 + 0.5


def tau_from_lattice_kinematic_viscosity(nu_lbm: float) -> float:
    return 3.0 * float(nu_lbm) + 0.5


def relaxation_semantics_summary(niu: float = 0.1) -> dict:
    return {
        "lbm_config_niu_semantics": LEGACY_EXTERNAL_SOLVER_RELAXATION_PARAMETER,
        "default_tau_convention": DEFAULT_TAU_CONVENTION,
        "standard_tau_convention": STANDARD_LATTICE_KINEMATIC_VISCOSITY,
        "legacy_tau_formula_name": "tau_from_legacy_external_solver_parameter",
        "standard_tau_formula_name": "tau_from_lattice_kinematic_viscosity",
        "legacy_tau_for_default_niu": tau_from_legacy_external_solver_parameter(niu),
        "standard_tau_for_default_nu_lbm": tau_from_lattice_kinematic_viscosity(niu),
        "default_solver_formula": "legacy_external_solver_parameter",
        "standard_lattice_viscosity_is_default": False,
        "physical_viscosity_validation_claim": False,
        "solver_behavior_changed": False,
    }
