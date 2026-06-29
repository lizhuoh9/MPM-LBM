from dataclasses import dataclass
from typing import Optional, Tuple

from .relaxation_semantics import (
    LEGACY_EXTERNAL_SOLVER_RELAXATION_PARAMETER,
    STANDARD_LATTICE_KINEMATIC_VISCOSITY,
)


VALID_LBM_RELAXATION_SEMANTICS = (
    LEGACY_EXTERNAL_SOLVER_RELAXATION_PARAMETER,
    STANDARD_LATTICE_KINEMATIC_VISCOSITY,
)

VALID_LBM_OPEN_BOUNDARY_SEMANTICS = (
    "equilibrium_all_population_reset",
    "regularized_velocity_pressure",
    "regularized_velocity_pressure_limited",
    "convective_pressure_outlet_experimental",
    "regularized_mass_balanced_pressure_outlet",
    "convective_mass_balanced_pressure_outlet",
    "regularized_flux_matched_pressure_outlet",
    "convective_flux_matched_damped_outlet",
    "regularized_plane_flux_controlled_pressure_outlet",
    "convective_plane_flux_controlled_damped_outlet",
)

VALID_OPEN_BOUNDARY_MASS_NEUTRAL_FLUX_CONTROL_MODES = (
    "disabled",
    "global_mass_error_density_offset",
    "outlet_population_projection_report_only",
)

VALID_OPEN_BOUNDARY_MASS_NEUTRAL_REFERENCE_MASS_MODES = ("initial",)


@dataclass
class LBMConfig:
    nx: int
    ny: int
    nz: int

    niu: float = 0.1
    rho0: float = 1.0
    relaxation_semantics: str = LEGACY_EXTERNAL_SOLVER_RELAXATION_PARAMETER
    open_boundary_semantics: str = "equilibrium_all_population_reset"
    open_boundary_limiter_enabled: bool = False
    open_boundary_rho_min: float = 0.8
    open_boundary_rho_max: float = 1.2
    open_boundary_u_max: float = 0.1
    open_boundary_noneq_cap: float = 0.05
    open_boundary_population_floor: Optional[float] = None
    open_boundary_flux_feedback_gain_u: float = 0.01
    open_boundary_flux_feedback_gain_rho: float = 0.005
    open_boundary_flux_filter_alpha: float = 0.05
    open_boundary_flux_correction_cap_u: float = 0.005
    open_boundary_flux_feedback_delta_cap_u: float = 0.0
    open_boundary_flux_feedback_slew_alpha: float = 1.0
    open_boundary_convective_blend_weight: float = 0.05
    open_boundary_flux_control_measure_plane_offset: int = 0
    open_boundary_flux_control_target_scale: float = 1.0
    open_boundary_outlet_flux_drop_guard_enabled: bool = False
    open_boundary_outlet_flux_drop_guard_min_ratio: float = 0.60
    open_boundary_mass_neutral_flux_control_enabled: bool = False
    open_boundary_mass_neutral_flux_control_mode: str = "disabled"
    open_boundary_mass_neutral_mass_error_gain: float = 0.0
    open_boundary_mass_neutral_mass_error_cap: float = 0.0
    open_boundary_mass_neutral_correction_blend: float = 0.0
    open_boundary_mass_neutral_reference_mass_mode: str = "initial"
    sparse_storage: bool = False

    force: Tuple[float, float, float] = (0.0, 0.0, 0.0)

    bc_x_left: int = 0
    bc_x_right: int = 0
    bc_y_left: int = 0
    bc_y_right: int = 0
    bc_z_left: int = 0
    bc_z_right: int = 0

    rho_bc_x_left: float = 1.0
    rho_bc_x_right: float = 1.0
    rho_bc_y_left: float = 1.0
    rho_bc_y_right: float = 1.0
    rho_bc_z_left: float = 1.0
    rho_bc_z_right: float = 1.0

    vel_bc_x_left: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    vel_bc_x_right: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    vel_bc_y_left: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    vel_bc_y_right: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    vel_bc_z_left: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    vel_bc_z_right: Tuple[float, float, float] = (0.0, 0.0, 0.0)

    def __post_init__(self):
        if self.relaxation_semantics not in VALID_LBM_RELAXATION_SEMANTICS:
            raise ValueError(f"relaxation_semantics must be one of {VALID_LBM_RELAXATION_SEMANTICS}")
        if self.open_boundary_semantics not in VALID_LBM_OPEN_BOUNDARY_SEMANTICS:
            raise ValueError(f"open_boundary_semantics must be one of {VALID_LBM_OPEN_BOUNDARY_SEMANTICS}")
        if self.open_boundary_rho_min <= 0.0:
            raise ValueError("open_boundary_rho_min must be positive")
        if self.open_boundary_rho_max <= self.open_boundary_rho_min:
            raise ValueError("open_boundary_rho_min must be less than open_boundary_rho_max")
        if self.open_boundary_u_max <= 0.0:
            raise ValueError("open_boundary_u_max must be positive")
        if self.open_boundary_noneq_cap <= 0.0:
            raise ValueError("open_boundary_noneq_cap must be positive")
        if self.open_boundary_flux_feedback_gain_u < 0.0:
            raise ValueError("open_boundary_flux_feedback_gain_u must be non-negative")
        if self.open_boundary_flux_feedback_gain_rho < 0.0:
            raise ValueError("open_boundary_flux_feedback_gain_rho must be non-negative")
        if not (0.0 < self.open_boundary_flux_filter_alpha <= 1.0):
            raise ValueError("open_boundary_flux_filter_alpha must be in (0, 1]")
        if self.open_boundary_flux_correction_cap_u <= 0.0:
            raise ValueError("open_boundary_flux_correction_cap_u must be positive")
        if self.open_boundary_flux_feedback_delta_cap_u < 0.0:
            raise ValueError("open_boundary_flux_feedback_delta_cap_u must be non-negative")
        if not (0.0 < self.open_boundary_flux_feedback_slew_alpha <= 1.0):
            raise ValueError("open_boundary_flux_feedback_slew_alpha must be in (0, 1]")
        if not (0.0 <= self.open_boundary_convective_blend_weight <= 1.0):
            raise ValueError("open_boundary_convective_blend_weight must be in [0, 1]")
        if int(self.open_boundary_flux_control_measure_plane_offset) != self.open_boundary_flux_control_measure_plane_offset:
            raise ValueError("open_boundary_flux_control_measure_plane_offset must be an integer")
        if not (0 <= int(self.open_boundary_flux_control_measure_plane_offset) <= 2):
            raise ValueError("open_boundary_flux_control_measure_plane_offset must be 0, 1, or 2")
        self.open_boundary_flux_control_measure_plane_offset = int(self.open_boundary_flux_control_measure_plane_offset)
        if self.open_boundary_flux_control_target_scale <= 0.0:
            raise ValueError("open_boundary_flux_control_target_scale must be positive")
        self.open_boundary_flux_control_target_scale = float(self.open_boundary_flux_control_target_scale)
        if not (0.0 < self.open_boundary_outlet_flux_drop_guard_min_ratio <= 1.0):
            raise ValueError("open_boundary_outlet_flux_drop_guard_min_ratio must be in (0, 1]")
        self.open_boundary_mass_neutral_flux_control_enabled = bool(
            self.open_boundary_mass_neutral_flux_control_enabled
        )
        if self.open_boundary_mass_neutral_flux_control_mode not in VALID_OPEN_BOUNDARY_MASS_NEUTRAL_FLUX_CONTROL_MODES:
            raise ValueError(
                "open_boundary_mass_neutral_flux_control_mode must be one of "
                f"{VALID_OPEN_BOUNDARY_MASS_NEUTRAL_FLUX_CONTROL_MODES}"
            )
        if (
            self.open_boundary_mass_neutral_reference_mass_mode
            not in VALID_OPEN_BOUNDARY_MASS_NEUTRAL_REFERENCE_MASS_MODES
        ):
            raise ValueError(
                "open_boundary_mass_neutral_reference_mass_mode must be one of "
                f"{VALID_OPEN_BOUNDARY_MASS_NEUTRAL_REFERENCE_MASS_MODES}"
            )
        if (
            self.open_boundary_mass_neutral_flux_control_enabled
            and self.open_boundary_mass_neutral_flux_control_mode == "disabled"
        ):
            raise ValueError("open_boundary_mass_neutral_flux_control_enabled cannot be true when mode is disabled")
        if self.open_boundary_mass_neutral_mass_error_gain < 0.0:
            raise ValueError("open_boundary_mass_neutral_mass_error_gain must be non-negative")
        if self.open_boundary_mass_neutral_mass_error_cap < 0.0:
            raise ValueError("open_boundary_mass_neutral_mass_error_cap must be non-negative")
        if not (0.0 <= self.open_boundary_mass_neutral_correction_blend <= 1.0):
            raise ValueError("open_boundary_mass_neutral_correction_blend must be in [0, 1]")
        self.open_boundary_mass_neutral_flux_control_mode = str(self.open_boundary_mass_neutral_flux_control_mode)
        self.open_boundary_mass_neutral_mass_error_gain = float(self.open_boundary_mass_neutral_mass_error_gain)
        self.open_boundary_mass_neutral_mass_error_cap = float(self.open_boundary_mass_neutral_mass_error_cap)
        self.open_boundary_mass_neutral_correction_blend = float(self.open_boundary_mass_neutral_correction_blend)
        self.open_boundary_mass_neutral_reference_mass_mode = str(
            self.open_boundary_mass_neutral_reference_mass_mode
        )
