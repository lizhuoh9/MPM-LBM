from dataclasses import dataclass
from typing import Optional

from ..lbm.config import LBMConfig
from ..mpm.config import MPMConfig


@dataclass(frozen=True)
class UnifiedSimConfig:
    n_grid: int = 32
    domain_length: float = 1.0
    mpm_dt: float = 4.0e-4
    mpm_substeps_per_lbm_step: int = 10
    lbm_niu: float = 0.1
    lbm_rho0: float = 1.0
    lbm_dt_phys_override_s: Optional[float] = None

    def __post_init__(self):
        if self.n_grid <= 0:
            raise ValueError("n_grid must be positive")
        if self.domain_length <= 0.0:
            raise ValueError("domain_length must be positive")
        if self.mpm_dt <= 0.0:
            raise ValueError("mpm_dt must be positive")
        if self.mpm_substeps_per_lbm_step <= 0:
            raise ValueError("mpm_substeps_per_lbm_step must be positive")
        if self.lbm_niu <= 0.0:
            raise ValueError("lbm_niu must be positive")
        if self.lbm_rho0 <= 0.0:
            raise ValueError("lbm_rho0 must be positive")
        if self.lbm_dt_phys_override_s is not None and self.lbm_dt_phys_override_s <= 0.0:
            raise ValueError("lbm_dt_phys_override_s must be positive when provided")

    @property
    def nx(self) -> int:
        return self.n_grid

    @property
    def ny(self) -> int:
        return self.n_grid

    @property
    def nz(self) -> int:
        return self.n_grid

    @property
    def dx_norm(self) -> float:
        return self.domain_length / float(self.n_grid)

    @property
    def lbm_dt_phys(self) -> float:
        if self.lbm_dt_phys_override_s is not None:
            return float(self.lbm_dt_phys_override_s)
        return self.mpm_substeps_per_lbm_step * self.mpm_dt

    def make_lbm_config(self, **overrides) -> LBMConfig:
        values = {
            "nx": self.nx,
            "ny": self.ny,
            "nz": self.nz,
            "niu": self.lbm_niu,
            "rho0": self.lbm_rho0,
        }
        values.update(overrides)
        return LBMConfig(**values)

    def make_mpm_config(self, **overrides) -> MPMConfig:
        values = {
            "n_grid": self.n_grid,
            "dx": self.dx_norm,
            "dt": self.mpm_dt,
        }
        values.update(overrides)
        return MPMConfig(**values)
