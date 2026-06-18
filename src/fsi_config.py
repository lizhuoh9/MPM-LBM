from dataclasses import asdict, dataclass
import json
from typing import Optional, Tuple

from .geometry_config import VALID_GEOMETRY_TYPES
from .sim_config import UnifiedSimConfig


VALID_COUPLING_MODES = ("none", "penalty", "moving_boundary")


def _as_float_tuple(values, name):
    if len(values) != 3:
        raise ValueError(f"{name} must contain exactly three values")
    return tuple(float(v) for v in values)


@dataclass(frozen=True)
class FSIDriverConfig:
    coupling_mode: str = "penalty"
    geometry_type: str = "box"
    geometry_config_path: Optional[str] = None

    n_grid: int = 32
    n_particles: int = 4096
    n_lbm_steps: int = 20
    mpm_substeps_per_lbm_step: int = 10
    mpm_dt: float = 4.0e-4

    target_u_lbm: Tuple[float, float, float] = (0.02, 0.0, 0.0)
    gravity: Tuple[float, float, float] = (0.0, 0.0, 0.0)

    box_min: Tuple[float, float, float] = (0.25, 0.35, 0.25)
    box_max: Tuple[float, float, float] = (0.55, 0.65, 0.55)

    dynamic_solid_threshold: float = 0.5

    beta_lbm: float = 1.0e-3
    penalty_force_cap_lbm: float = 1.0e-4

    mb_reaction_scale: float = 1.0
    mb_force_cap_norm: float = 1.0e-4

    output_interval: int = 10
    write_vtk: bool = True
    write_particles: bool = True

    def __post_init__(self):
        if self.coupling_mode not in VALID_COUPLING_MODES:
            raise ValueError(f"coupling_mode must be one of {VALID_COUPLING_MODES}")
        if self.geometry_type not in VALID_GEOMETRY_TYPES:
            raise ValueError(f"geometry_type must be one of {VALID_GEOMETRY_TYPES}")
        if self.n_grid <= 0:
            raise ValueError("n_grid must be positive")
        if self.n_particles <= 0:
            raise ValueError("n_particles must be positive")
        if self.n_lbm_steps <= 0:
            raise ValueError("n_lbm_steps must be positive")
        if self.mpm_substeps_per_lbm_step <= 0:
            raise ValueError("mpm_substeps_per_lbm_step must be positive")
        if self.mpm_dt <= 0.0:
            raise ValueError("mpm_dt must be positive")
        if self.dynamic_solid_threshold < 0.0:
            raise ValueError("dynamic_solid_threshold must be non-negative")
        if self.beta_lbm <= 0.0:
            raise ValueError("beta_lbm must be positive")
        if self.penalty_force_cap_lbm <= 0.0:
            raise ValueError("penalty_force_cap_lbm must be positive")
        if self.mb_reaction_scale <= 0.0:
            raise ValueError("mb_reaction_scale must be positive")
        if self.mb_force_cap_norm <= 0.0:
            raise ValueError("mb_force_cap_norm must be positive")
        if self.output_interval <= 0:
            raise ValueError("output_interval must be positive")

        object.__setattr__(self, "target_u_lbm", _as_float_tuple(self.target_u_lbm, "target_u_lbm"))
        object.__setattr__(self, "gravity", _as_float_tuple(self.gravity, "gravity"))
        object.__setattr__(self, "box_min", _as_float_tuple(self.box_min, "box_min"))
        object.__setattr__(self, "box_max", _as_float_tuple(self.box_max, "box_max"))

    @classmethod
    def from_json(cls, path):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls(**data)

    def to_dict(self):
        data = asdict(self)
        for key in ("target_u_lbm", "gravity", "box_min", "box_max"):
            data[key] = list(data[key])
        return data

    def make_unified_sim_config(self):
        return UnifiedSimConfig(
            n_grid=self.n_grid,
            mpm_dt=self.mpm_dt,
            mpm_substeps_per_lbm_step=self.mpm_substeps_per_lbm_step,
        )
