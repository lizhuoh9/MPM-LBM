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
)


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
