from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Optional, Tuple

from .geometry_config import VALID_GEOMETRY_TYPES
from .sim_config import UnifiedSimConfig


VALID_COUPLING_MODES = ("none", "penalty", "moving_boundary")
VALID_REACTION_TRANSFER_MODES = ("engineering", "link_area_experimental")
VALID_LINK_AREA_POLICIES = ("uniform", "inverse_length", "length")
VALID_BOUNDARY_MOTION_MODES = ("static", "prescribed_kinematic")
VALID_WALL_VELOCITY_APPLICATION_MODES = ("disabled", "solid_vel_experimental")
VALID_GEOMETRY_MOTION_MODES = ("static", "prescribed_kinematic")
VALID_GEOMETRY_MOTION_APPLICATION_MODES = ("disabled", "diagnostic_only")


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
    reaction_transfer_mode: str = "engineering"
    link_area_policy: str = "inverse_length"
    link_area_scale_min: float = 0.25
    link_area_scale_max: float = 2.0
    boundary_motion_mode: str = "static"
    boundary_motion_config_path: Optional[str] = None
    boundary_motion_report_enabled: bool = False
    wall_velocity_application_mode: str = "disabled"
    wall_velocity_application_config_path: Optional[str] = None
    wall_velocity_application_report_enabled: bool = False
    geometry_motion_mode: str = "static"
    geometry_motion_config_path: Optional[str] = None
    geometry_motion_report_enabled: bool = False
    geometry_motion_application_mode: str = "disabled"
    geometry_motion_application_config_path: Optional[str] = None
    geometry_motion_application_report_enabled: bool = False

    output_interval: int = 10
    write_vtk: bool = True
    write_particles: bool = True
    quality_check_enabled: bool = False
    quality_check_strict: bool = False
    quality_report_path: Optional[str] = None

    def __post_init__(self):
        if self.coupling_mode not in VALID_COUPLING_MODES:
            raise ValueError(f"coupling_mode must be one of {VALID_COUPLING_MODES}")
        if self.reaction_transfer_mode not in VALID_REACTION_TRANSFER_MODES:
            raise ValueError(f"reaction_transfer_mode must be one of {VALID_REACTION_TRANSFER_MODES}")
        if self.reaction_transfer_mode == "link_area_experimental" and self.coupling_mode != "moving_boundary":
            raise ValueError("reaction_transfer_mode='link_area_experimental' requires coupling_mode='moving_boundary'")
        if self.link_area_policy not in VALID_LINK_AREA_POLICIES:
            raise ValueError(f"link_area_policy must be one of {VALID_LINK_AREA_POLICIES}")
        if self.boundary_motion_mode not in VALID_BOUNDARY_MOTION_MODES:
            raise ValueError(f"boundary_motion_mode must be one of {VALID_BOUNDARY_MOTION_MODES}")
        if self.boundary_motion_mode == "static" and self.boundary_motion_config_path is not None:
            raise ValueError("boundary_motion_config_path must be None when boundary_motion_mode='static'")
        if self.boundary_motion_mode == "prescribed_kinematic" and not self.boundary_motion_config_path:
            raise ValueError("boundary_motion_config_path is required when boundary_motion_mode='prescribed_kinematic'")
        if self.wall_velocity_application_mode not in VALID_WALL_VELOCITY_APPLICATION_MODES:
            raise ValueError(f"wall_velocity_application_mode must be one of {VALID_WALL_VELOCITY_APPLICATION_MODES}")
        if self.wall_velocity_application_mode == "disabled" and self.wall_velocity_application_config_path is not None:
            raise ValueError("wall_velocity_application_config_path must be None when wall_velocity_application_mode='disabled'")
        if self.wall_velocity_application_mode == "solid_vel_experimental":
            if self.boundary_motion_mode != "prescribed_kinematic":
                raise ValueError("wall_velocity_application_mode='solid_vel_experimental' requires boundary_motion_mode='prescribed_kinematic'")
            if not self.wall_velocity_application_config_path:
                raise ValueError("wall_velocity_application_config_path is required when wall_velocity_application_mode='solid_vel_experimental'")
            if not _path_exists(self.wall_velocity_application_config_path):
                raise ValueError("wall_velocity_application_config_path must exist when wall_velocity_application_mode='solid_vel_experimental'")
        if self.geometry_motion_mode not in VALID_GEOMETRY_MOTION_MODES:
            raise ValueError(f"geometry_motion_mode must be one of {VALID_GEOMETRY_MOTION_MODES}")
        if self.geometry_motion_application_mode not in VALID_GEOMETRY_MOTION_APPLICATION_MODES:
            raise ValueError(f"geometry_motion_application_mode must be one of {VALID_GEOMETRY_MOTION_APPLICATION_MODES}")
        if self.geometry_motion_mode == "static":
            if self.geometry_motion_config_path is not None:
                raise ValueError("geometry_motion_config_path must be None when geometry_motion_mode='static'")
            if self.geometry_motion_application_mode != "disabled":
                raise ValueError("geometry_motion_application_mode must be disabled when geometry_motion_mode='static'")
        if self.geometry_motion_mode == "prescribed_kinematic":
            if not self.geometry_motion_config_path:
                raise ValueError("geometry_motion_config_path is required when geometry_motion_mode='prescribed_kinematic'")
            if not _path_exists(self.geometry_motion_config_path):
                raise ValueError("geometry_motion_config_path must exist when geometry_motion_mode='prescribed_kinematic'")
        if self.geometry_motion_application_mode == "disabled" and self.geometry_motion_application_config_path is not None:
            raise ValueError("geometry_motion_application_config_path must be None when geometry_motion_application_mode='disabled'")
        if self.geometry_motion_application_mode == "diagnostic_only":
            if self.geometry_motion_mode != "prescribed_kinematic":
                raise ValueError("geometry_motion_application_mode='diagnostic_only' requires geometry_motion_mode='prescribed_kinematic'")
            if not self.geometry_motion_application_config_path:
                raise ValueError("geometry_motion_application_config_path is required when geometry_motion_application_mode='diagnostic_only'")
            if not _path_exists(self.geometry_motion_application_config_path):
                raise ValueError("geometry_motion_application_config_path must exist when geometry_motion_application_mode='diagnostic_only'")
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
        if self.link_area_scale_min <= 0.0:
            raise ValueError("link_area_scale_min must be positive")
        if self.link_area_scale_max <= 0.0:
            raise ValueError("link_area_scale_max must be positive")
        if self.link_area_scale_min > self.link_area_scale_max:
            raise ValueError("link_area_scale_min must be <= link_area_scale_max")
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


def _path_exists(path) -> bool:
    path_obj = Path(path)
    if path_obj.is_absolute():
        return path_obj.is_file()
    return (_repo_root() / path_obj).is_file() or path_obj.is_file()


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]
