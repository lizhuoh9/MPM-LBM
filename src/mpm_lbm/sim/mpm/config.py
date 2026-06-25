from dataclasses import dataclass
from typing import Tuple


@dataclass
class MPMConfig:
    n_grid: int = 32
    dx: float = 1.0 / 32.0
    dt: float = 4.0e-4

    gravity: Tuple[float, float, float] = (0.0, -9.8, 0.0)

    p_rho: float = 1.0
    particles_per_cell: int = 2

    young_modulus: float = 400.0
    poisson_ratio: float = 0.2

    bound: int = 3
    use_apic: bool = True

    box_min: Tuple[float, float, float] = (0.25, 0.35, 0.25)
    box_max: Tuple[float, float, float] = (0.55, 0.65, 0.55)

    mpm_planar_constraint_mode: str = "disabled"
    mpm_planar_constraint_axis: str = "z"
    mpm_velocity_damping: float = 0.0
    mpm_damping_application: str = "disabled"

    output_interval: int = 10
