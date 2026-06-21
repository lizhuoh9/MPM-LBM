from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class GridUnitMapper:
    n_grid: int
    dx_norm: float
    lbm_dt_phys: float

    def __post_init__(self):
        if self.n_grid <= 0:
            raise ValueError("n_grid must be positive")
        if self.dx_norm <= 0.0:
            raise ValueError("dx_norm must be positive")
        if self.lbm_dt_phys <= 0.0:
            raise ValueError("lbm_dt_phys must be positive")

    @classmethod
    def from_sim_config(cls, sim_config):
        return cls(
            n_grid=sim_config.n_grid,
            dx_norm=sim_config.dx_norm,
            lbm_dt_phys=sim_config.lbm_dt_phys,
        )

    def norm_to_lbm_coord(self, x_norm):
        return np.asarray(x_norm, dtype=np.float64) / self.dx_norm

    def lbm_coord_to_norm(self, x_lbm):
        return np.asarray(x_lbm, dtype=np.float64) * self.dx_norm

    def norm_to_lbm_index(self, x_norm):
        idx = np.floor(self.norm_to_lbm_coord(x_norm)).astype(np.int32)
        return np.clip(idx, 0, self.n_grid - 1)

    def lbm_index_to_norm_center(self, idx):
        return (np.asarray(idx, dtype=np.float64) + 0.5) * self.dx_norm

    def velocity_norm_to_lbm(self, v_norm):
        return np.asarray(v_norm, dtype=np.float64) * self.lbm_dt_phys / self.dx_norm

    def velocity_lbm_to_norm(self, v_lbm):
        return np.asarray(v_lbm, dtype=np.float64) * self.dx_norm / self.lbm_dt_phys

    def acceleration_norm_to_lbm(self, a_norm):
        return np.asarray(a_norm, dtype=np.float64) * self.lbm_dt_phys**2 / self.dx_norm

    def acceleration_lbm_to_norm(self, a_lbm):
        return np.asarray(a_lbm, dtype=np.float64) * self.dx_norm / self.lbm_dt_phys**2

    def viscosity_norm_to_lbm(self, nu_norm):
        return float(nu_norm) * self.lbm_dt_phys / (self.dx_norm**2)

    def viscosity_lbm_to_norm(self, nu_lbm):
        return float(nu_lbm) * (self.dx_norm**2) / self.lbm_dt_phys
