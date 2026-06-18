from dataclasses import dataclass
from typing import Tuple


@dataclass
class LBMConfig:
    nx: int
    ny: int
    nz: int

    niu: float = 0.1
    rho0: float = 1.0
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
