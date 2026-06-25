from dataclasses import asdict, dataclass
import json
import math
from pathlib import Path
from typing import Optional, Tuple

from ..geometry.config import VALID_GEOMETRY_TYPES
from ..lbm.relaxation_semantics import (
    LEGACY_EXTERNAL_SOLVER_RELAXATION_PARAMETER,
    STANDARD_LATTICE_KINEMATIC_VISCOSITY,
    tau_from_lattice_kinematic_viscosity,
    tau_from_legacy_external_solver_parameter,
)
from .sim_config import UnifiedSimConfig


VALID_COUPLING_MODES = ("none", "penalty", "moving_boundary")
VALID_REACTION_TRANSFER_MODES = ("engineering", "link_area_experimental", "interface_traction_conservative")
VALID_LINK_AREA_POLICIES = ("uniform", "inverse_length", "length")
VALID_BOUNDARY_MOTION_MODES = ("static", "prescribed_kinematic")
VALID_WALL_VELOCITY_APPLICATION_MODES = ("disabled", "solid_vel_experimental")
VALID_GEOMETRY_MOTION_MODES = ("static", "prescribed_kinematic")
VALID_GEOMETRY_MOTION_APPLICATION_MODES = ("disabled", "diagnostic_only")
VALID_LBM_BOUNDARY_CONDITION_MODES = ("default_periodic", "duct_velocity_inlet_pressure_outlet")
VALID_LBM_OPEN_BOUNDARY_SEMANTICS = (
    "equilibrium_all_population_reset",
    "zou_he_reconstruct_unknowns",
    "regularized_velocity_pressure",
)
IMPLEMENTED_LBM_OPEN_BOUNDARY_SEMANTICS = (
    "equilibrium_all_population_reset",
    "regularized_velocity_pressure",
)
VALID_LBM_VISCOSITY_SEMANTICS = ("legacy_external", "physical_nu_mapping")
VALID_LBM_TAU_STABILITY_POLICIES = ("report_only", "strict")
VALID_FSI_EXCHANGE_MODES = ("one_lbm_step_per_fsi_step", "lbm_subcycled_per_fsi_step")
VALID_LBM_RESTART_SCOPES = ("rho_velocity_populations",)
VALID_MPM_PLANAR_CONSTRAINT_MODES = ("disabled", "lock_z")
VALID_MPM_PLANAR_CONSTRAINT_AXES = ("z",)
VALID_MPM_DAMPING_APPLICATIONS = ("disabled", "particle_velocity_post_g2p")
VALID_SOLID_MODELS = ("finite_deformation_mpm", "small_strain_linear_elastic")
IMPLEMENTED_SOLID_MODELS = ("finite_deformation_mpm",)
VALID_SOLID_DIMENSIONALITIES = ("three_dimensional", "plane_strain_2d", "plane_stress_2d")
IMPLEMENTED_SOLID_DIMENSIONALITIES = ("three_dimensional",)
VALID_FLOW_DIMENSIONALITY_MODES = ("three_dimensional", "thin_3d_no_slip_z_walls", "d2q9_planar", "d3q19_quasi_2d_periodic_z")
IMPLEMENTED_FLOW_DIMENSIONALITY_MODES = ("three_dimensional", "thin_3d_no_slip_z_walls")
VALID_BOUNDARY_AXES = ("x",)
VALID_BOUNDARY_SIDES = ("min", "max")


def _as_float_tuple(values, name):
    if len(values) != 3:
        raise ValueError(f"{name} must contain exactly three values")
    return tuple(float(v) for v in values)


def _as_float_pair(values, name):
    if len(values) != 2:
        raise ValueError(f"{name} must contain exactly two values")
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
    initial_solid_velocity_norm: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    gravity: Tuple[float, float, float] = (0.0, 0.0, 0.0)

    lbm_boundary_condition_mode: str = "default_periodic"
    lbm_open_boundary_semantics: str = "equilibrium_all_population_reset"
    velocity_inlet_axis: str = "x"
    velocity_inlet_side: str = "min"
    pressure_outlet_side: str = "max"
    physical_duct_length_m: float = 1.0
    target_inlet_velocity_mps: Optional[float] = None
    official_fsi_dt_s: Optional[float] = None
    target_u_lbm_for_dimensional_mapping: Optional[float] = None
    lbm_substeps_per_fsi_step: int = 1
    lbm_dt_phys_override_s: Optional[float] = None
    fluid_density_kg_m3: float = 1.225
    fluid_kinematic_viscosity_m2_s: float = 1.5e-5
    target_reynolds_number: Optional[float] = None
    lbm_viscosity_semantics: str = "legacy_external"
    lbm_min_tau_margin: float = 1.0e-4
    lbm_tau_stability_policy: str = "report_only"
    fsi_exchange_mode: str = "one_lbm_step_per_fsi_step"
    lbm_restart_path: Optional[str] = None
    lbm_restart_required: bool = False
    lbm_restart_scope: str = "rho_velocity_populations"

    box_min: Tuple[float, float, float] = (0.25, 0.35, 0.25)
    box_max: Tuple[float, float, float] = (0.55, 0.65, 0.55)

    dynamic_solid_threshold: float = 0.5

    beta_lbm: float = 1.0e-3
    penalty_force_cap_lbm: float = 1.0e-4

    mb_reaction_scale: float = 1.0
    mb_force_cap_norm: float = 1.0e-4
    reaction_transfer_mode: str = "engineering"
    solid_model: str = "finite_deformation_mpm"
    solid_dimensionality: str = "three_dimensional"
    flow_dimensionality_mode: str = "three_dimensional"
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

    mpm_planar_constraint_mode: str = "disabled"
    mpm_planar_constraint_axis: str = "z"
    mpm_velocity_damping: float = 0.0
    mpm_damping_application: str = "disabled"

    fluent_like_monitor_enabled: bool = False
    fluent_like_monitor_physical_point_m: Tuple[float, float] = (0.0505, 0.0095)
    fluent_like_monitor_nearest_count: int = 8
    fluent_like_monitor_radius_m: Optional[float] = None

    output_interval: int = 10
    write_vtk: bool = False
    write_particles: bool = False
    quality_check_enabled: bool = False
    quality_check_strict: bool = False
    quality_report_path: Optional[str] = None

    def __post_init__(self):
        object.__setattr__(self, "target_u_lbm", _as_float_tuple(self.target_u_lbm, "target_u_lbm"))
        object.__setattr__(
            self,
            "initial_solid_velocity_norm",
            _as_float_tuple(self.initial_solid_velocity_norm, "initial_solid_velocity_norm"),
        )
        object.__setattr__(self, "gravity", _as_float_tuple(self.gravity, "gravity"))
        object.__setattr__(self, "box_min", _as_float_tuple(self.box_min, "box_min"))
        object.__setattr__(self, "box_max", _as_float_tuple(self.box_max, "box_max"))
        object.__setattr__(
            self,
            "fluent_like_monitor_physical_point_m",
            _as_float_pair(self.fluent_like_monitor_physical_point_m, "fluent_like_monitor_physical_point_m"),
        )

        if self.coupling_mode not in VALID_COUPLING_MODES:
            raise ValueError(f"coupling_mode must be one of {VALID_COUPLING_MODES}")
        if self.reaction_transfer_mode not in VALID_REACTION_TRANSFER_MODES:
            raise ValueError(f"reaction_transfer_mode must be one of {VALID_REACTION_TRANSFER_MODES}")
        if self.reaction_transfer_mode == "interface_traction_conservative":
            raise ValueError("reaction_transfer_mode='interface_traction_conservative' is planned but not implemented")
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
        if self.mpm_planar_constraint_mode not in VALID_MPM_PLANAR_CONSTRAINT_MODES:
            raise ValueError(f"mpm_planar_constraint_mode must be one of {VALID_MPM_PLANAR_CONSTRAINT_MODES}")
        if self.mpm_planar_constraint_axis not in VALID_MPM_PLANAR_CONSTRAINT_AXES:
            raise ValueError(f"mpm_planar_constraint_axis must be one of {VALID_MPM_PLANAR_CONSTRAINT_AXES}")
        if float(self.mpm_velocity_damping) < 0.0:
            raise ValueError("mpm_velocity_damping must be non-negative")
        if self.mpm_damping_application not in VALID_MPM_DAMPING_APPLICATIONS:
            raise ValueError(f"mpm_damping_application must be one of {VALID_MPM_DAMPING_APPLICATIONS}")
        if self.mpm_damping_application == "disabled" and float(self.mpm_velocity_damping) != 0.0:
            raise ValueError("mpm_velocity_damping must be 0 when mpm_damping_application is disabled")
        if self.mpm_damping_application == "particle_velocity_post_g2p" and float(self.mpm_velocity_damping) <= 0.0:
            raise ValueError("mpm_velocity_damping must be positive when damping is enabled")
        if self.geometry_type not in VALID_GEOMETRY_TYPES:
            raise ValueError(f"geometry_type must be one of {VALID_GEOMETRY_TYPES}")
        if self.lbm_boundary_condition_mode not in VALID_LBM_BOUNDARY_CONDITION_MODES:
            raise ValueError(f"lbm_boundary_condition_mode must be one of {VALID_LBM_BOUNDARY_CONDITION_MODES}")
        if self.lbm_open_boundary_semantics not in VALID_LBM_OPEN_BOUNDARY_SEMANTICS:
            raise ValueError(f"lbm_open_boundary_semantics must be one of {VALID_LBM_OPEN_BOUNDARY_SEMANTICS}")
        if self.lbm_open_boundary_semantics not in IMPLEMENTED_LBM_OPEN_BOUNDARY_SEMANTICS:
            raise ValueError(f"lbm_open_boundary_semantics={self.lbm_open_boundary_semantics!r} is not implemented")
        if self.lbm_viscosity_semantics not in VALID_LBM_VISCOSITY_SEMANTICS:
            raise ValueError(f"lbm_viscosity_semantics must be one of {VALID_LBM_VISCOSITY_SEMANTICS}")
        if self.lbm_tau_stability_policy not in VALID_LBM_TAU_STABILITY_POLICIES:
            raise ValueError(f"lbm_tau_stability_policy must be one of {VALID_LBM_TAU_STABILITY_POLICIES}")
        if float(self.lbm_min_tau_margin) <= 0.0:
            raise ValueError("lbm_min_tau_margin must be positive")
        if self.solid_model not in VALID_SOLID_MODELS:
            raise ValueError(f"solid_model must be one of {VALID_SOLID_MODELS}")
        if self.solid_model not in IMPLEMENTED_SOLID_MODELS:
            raise ValueError(f"solid_model={self.solid_model!r} is not implemented")
        if self.solid_dimensionality not in VALID_SOLID_DIMENSIONALITIES:
            raise ValueError(f"solid_dimensionality must be one of {VALID_SOLID_DIMENSIONALITIES}")
        if self.solid_dimensionality not in IMPLEMENTED_SOLID_DIMENSIONALITIES:
            raise ValueError(f"solid_dimensionality={self.solid_dimensionality!r} is not implemented")
        if self.flow_dimensionality_mode not in VALID_FLOW_DIMENSIONALITY_MODES:
            raise ValueError(f"flow_dimensionality_mode must be one of {VALID_FLOW_DIMENSIONALITY_MODES}")
        if self.flow_dimensionality_mode not in IMPLEMENTED_FLOW_DIMENSIONALITY_MODES:
            raise ValueError(f"flow_dimensionality_mode={self.flow_dimensionality_mode!r} is not implemented")
        if self.velocity_inlet_axis not in VALID_BOUNDARY_AXES:
            raise ValueError(f"velocity_inlet_axis must be one of {VALID_BOUNDARY_AXES}")
        if self.velocity_inlet_side not in VALID_BOUNDARY_SIDES:
            raise ValueError(f"velocity_inlet_side must be one of {VALID_BOUNDARY_SIDES}")
        if self.pressure_outlet_side not in VALID_BOUNDARY_SIDES:
            raise ValueError(f"pressure_outlet_side must be one of {VALID_BOUNDARY_SIDES}")
        if self.fsi_exchange_mode not in VALID_FSI_EXCHANGE_MODES:
            raise ValueError(f"fsi_exchange_mode must be one of {VALID_FSI_EXCHANGE_MODES}")
        if self.lbm_restart_scope not in VALID_LBM_RESTART_SCOPES:
            raise ValueError(f"lbm_restart_scope must be one of {VALID_LBM_RESTART_SCOPES}")
        if self.lbm_restart_required and not self.lbm_restart_path:
            raise ValueError("lbm_restart_path is required when lbm_restart_required is true")
        if self.lbm_boundary_condition_mode == "duct_velocity_inlet_pressure_outlet":
            if self.velocity_inlet_axis != "x":
                raise ValueError("duct_velocity_inlet_pressure_outlet currently supports only x-axis inlet/outlet")
            if self.velocity_inlet_side == self.pressure_outlet_side:
                raise ValueError("velocity_inlet_side and pressure_outlet_side must differ")
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
        if self.physical_duct_length_m <= 0.0:
            raise ValueError("physical_duct_length_m must be positive")
        if self.lbm_substeps_per_fsi_step <= 0:
            raise ValueError("lbm_substeps_per_fsi_step must be positive")
        _validate_optional_positive(self.target_inlet_velocity_mps, "target_inlet_velocity_mps")
        _validate_optional_positive(self.official_fsi_dt_s, "official_fsi_dt_s")
        _validate_optional_positive(self.target_u_lbm_for_dimensional_mapping, "target_u_lbm_for_dimensional_mapping")
        _validate_optional_positive(self.lbm_dt_phys_override_s, "lbm_dt_phys_override_s")
        if self.fluid_density_kg_m3 <= 0.0:
            raise ValueError("fluid_density_kg_m3 must be positive")
        if self.fluid_kinematic_viscosity_m2_s <= 0.0:
            raise ValueError("fluid_kinematic_viscosity_m2_s must be positive")
        _validate_optional_positive(self.target_reynolds_number, "target_reynolds_number")
        _validate_optional_positive(self.fluent_like_monitor_radius_m, "fluent_like_monitor_radius_m")
        if self.fluent_like_monitor_nearest_count <= 0:
            raise ValueError("fluent_like_monitor_nearest_count must be positive")
        self._validate_fsi_exchange_mapping()
        self._validate_lbm_viscosity_mapping()
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

    def _validate_fsi_exchange_mapping(self) -> None:
        if self.fsi_exchange_mode == "one_lbm_step_per_fsi_step":
            if self.lbm_substeps_per_fsi_step != 1:
                raise ValueError("lbm_substeps_per_fsi_step must be 1 when fsi_exchange_mode='one_lbm_step_per_fsi_step'")
            if self.lbm_dt_phys_override_s is not None:
                raise ValueError("lbm_dt_phys_override_s requires fsi_exchange_mode='lbm_subcycled_per_fsi_step'")
            return

        if self.coupling_mode != "moving_boundary":
            raise ValueError("lbm_subcycled_per_fsi_step currently requires coupling_mode='moving_boundary'")
        missing = [
            name
            for name, value in (
                ("target_inlet_velocity_mps", self.target_inlet_velocity_mps),
                ("official_fsi_dt_s", self.official_fsi_dt_s),
                ("target_u_lbm_for_dimensional_mapping", self.target_u_lbm_for_dimensional_mapping),
                ("lbm_dt_phys_override_s", self.lbm_dt_phys_override_s),
            )
            if value is None
        ]
        if missing:
            raise ValueError("subcycled FSI exchange requires: " + ", ".join(missing))

        expected_official_dt = float(self.lbm_substeps_per_fsi_step) * float(self.lbm_dt_phys_override_s)
        if not math.isclose(float(self.official_fsi_dt_s), expected_official_dt, rel_tol=1.0e-12, abs_tol=1.0e-15):
            raise ValueError("official_fsi_dt_s must equal lbm_substeps_per_fsi_step * lbm_dt_phys_override_s")
        if not math.isclose(float(self.target_u_lbm[0]), float(self.target_u_lbm_for_dimensional_mapping), rel_tol=1.0e-12, abs_tol=1.0e-15):
            raise ValueError("target_u_lbm[0] must equal target_u_lbm_for_dimensional_mapping")
        dx_phys_m = float(self.physical_duct_length_m) / float(self.n_grid)
        mapped_velocity = float(self.target_u_lbm_for_dimensional_mapping) * dx_phys_m / float(self.lbm_dt_phys_override_s)
        if not math.isclose(mapped_velocity, float(self.target_inlet_velocity_mps), rel_tol=1.0e-12, abs_tol=1.0e-9):
            raise ValueError("dimensional mapping does not recover target_inlet_velocity_mps")

    def _validate_lbm_viscosity_mapping(self) -> None:
        mapping = self.lbm_viscosity_mapping_report()
        if not math.isfinite(float(mapping["tau"])) or float(mapping["tau"]) <= 0.5:
            raise ValueError("LBM viscosity mapping must produce finite tau > 0.5")
        if not math.isfinite(float(mapping["lbm_niu"])) or float(mapping["lbm_niu"]) <= 0.0:
            raise ValueError("LBM viscosity mapping must produce finite positive lbm_niu")
        if self.lbm_tau_stability_policy == "strict" and not bool(mapping["tau_margin_pass"]):
            raise ValueError("LBM tau stability margin failed strict policy")

    def lbm_viscosity_mapping_report(self) -> dict:
        if self.lbm_viscosity_semantics == "legacy_external":
            legacy_niu = 0.1
            tau = tau_from_legacy_external_solver_parameter(legacy_niu)
            tau_minus_half = float(tau) - 0.5
            tau_margin_pass = tau_minus_half >= float(self.lbm_min_tau_margin)
            reynolds_from_config = self._reynolds_from_config()
            return {
                "lbm_viscosity_semantics": self.lbm_viscosity_semantics,
                "physical_mapping_used": False,
                "fluid_density_kg_m3": float(self.fluid_density_kg_m3),
                "fluid_density_used_for_lbm_rho0": False,
                "fluid_kinematic_viscosity_m2_s": float(self.fluid_kinematic_viscosity_m2_s),
                "target_reynolds_number": None if self.target_reynolds_number is None else float(self.target_reynolds_number),
                "legacy_lbm_niu": legacy_niu,
                "nu_lbm": None,
                "lbm_niu": legacy_niu,
                "tau": tau,
                "tau_minus_half": tau_minus_half,
                "lbm_min_tau_margin": float(self.lbm_min_tau_margin),
                "lbm_tau_stability_policy": self.lbm_tau_stability_policy,
                "tau_margin_pass": tau_margin_pass,
                "lbm_relaxation_semantics": LEGACY_EXTERNAL_SOLVER_RELAXATION_PARAMETER,
                "mach_proxy": self._mach_proxy(),
                "reynolds_from_config": reynolds_from_config,
                "target_reynolds_match": self._target_reynolds_match(reynolds_from_config),
                "physical_reynolds_direct_simulation_feasible_with_current_lbm": None,
                "physical_viscosity_validation_claim": False,
            }

        if self.lbm_viscosity_semantics != "physical_nu_mapping":
            raise ValueError(f"unsupported lbm_viscosity_semantics: {self.lbm_viscosity_semantics}")

        dx_phys_m = float(self.physical_duct_length_m) / float(self.n_grid)
        dt_phys_s = float(
            self.lbm_dt_phys_override_s
            if self.lbm_dt_phys_override_s is not None
            else self.mpm_substeps_per_lbm_step * self.mpm_dt
        )
        nu_lbm = float(self.fluid_kinematic_viscosity_m2_s) * dt_phys_s / (dx_phys_m * dx_phys_m)
        tau = tau_from_lattice_kinematic_viscosity(nu_lbm)
        tau_minus_half = float(tau) - 0.5
        tau_margin_pass = tau_minus_half >= float(self.lbm_min_tau_margin)
        mach_proxy = self._mach_proxy()
        reynolds_from_config = self._reynolds_from_config()
        return {
            "lbm_viscosity_semantics": self.lbm_viscosity_semantics,
            "physical_mapping_used": True,
            "fluid_density_kg_m3": float(self.fluid_density_kg_m3),
            "fluid_density_used_for_lbm_rho0": False,
            "fluid_kinematic_viscosity_m2_s": float(self.fluid_kinematic_viscosity_m2_s),
            "target_reynolds_number": None if self.target_reynolds_number is None else float(self.target_reynolds_number),
            "dx_phys_m": dx_phys_m,
            "dt_phys_s": dt_phys_s,
            "nu_lbm": nu_lbm,
            "lbm_niu": nu_lbm,
            "tau": tau,
            "tau_minus_half": tau_minus_half,
            "lbm_min_tau_margin": float(self.lbm_min_tau_margin),
            "lbm_tau_stability_policy": self.lbm_tau_stability_policy,
            "tau_margin_pass": tau_margin_pass,
            "lbm_relaxation_semantics": STANDARD_LATTICE_KINEMATIC_VISCOSITY,
            "mach_proxy": mach_proxy,
            "reynolds_from_config": reynolds_from_config,
            "target_reynolds_match": self._target_reynolds_match(reynolds_from_config),
            "physical_reynolds_direct_simulation_feasible_with_current_lbm": bool(
                tau_margin_pass and mach_proxy <= 0.2
            ),
            "physical_viscosity_validation_claim": False,
        }

    def _mach_proxy(self) -> float:
        cs_lbm = math.sqrt(1.0 / 3.0)
        return float(math.sqrt(sum(float(v) * float(v) for v in self.target_u_lbm)) / cs_lbm)

    def _reynolds_from_config(self) -> Optional[float]:
        duct_height = self._duct_height_for_reynolds()
        if self.target_inlet_velocity_mps is None or duct_height is None:
            return None
        return float(self.target_inlet_velocity_mps) * duct_height / float(self.fluid_kinematic_viscosity_m2_s)

    def _target_reynolds_match(self, reynolds_from_config: Optional[float]) -> Optional[bool]:
        if self.target_reynolds_number is None or reynolds_from_config is None:
            return None
        return math.isclose(
            reynolds_from_config,
            float(self.target_reynolds_number),
            rel_tol=1.0e-9,
            abs_tol=1.0e-9,
        )

    def _duct_height_for_reynolds(self) -> Optional[float]:
        if self.geometry_config_path:
            path = Path(self.geometry_config_path)
            if not path.is_absolute():
                path = _repo_root() / path
            if path.is_file():
                with path.open("r", encoding="utf-8") as f:
                    data = json.load(f)
                dimensional = data.get("dimensional_reference") or {}
                if "duct_height_m" in dimensional:
                    return float(dimensional["duct_height_m"])
        return None

    @classmethod
    def from_json(cls, path):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls(**data)

    def to_dict(self):
        data = asdict(self)
        for key in (
            "target_u_lbm",
            "initial_solid_velocity_norm",
            "gravity",
            "box_min",
            "box_max",
            "fluent_like_monitor_physical_point_m",
        ):
            data[key] = list(data[key])
        return data

    def make_unified_sim_config(self):
        viscosity_mapping = self.lbm_viscosity_mapping_report()
        return UnifiedSimConfig(
            n_grid=self.n_grid,
            mpm_dt=self.mpm_dt,
            mpm_substeps_per_lbm_step=self.mpm_substeps_per_lbm_step,
            lbm_dt_phys_override_s=self.lbm_dt_phys_override_s,
            lbm_niu=float(viscosity_mapping["lbm_niu"]),
            lbm_rho0=1.0,
            lbm_relaxation_semantics=str(viscosity_mapping["lbm_relaxation_semantics"]),
            lbm_open_boundary_semantics=self.lbm_open_boundary_semantics,
        )

    def make_mpm_control_overrides(self):
        return {
            "mpm_damping_application": self.mpm_damping_application,
            "mpm_planar_constraint_axis": self.mpm_planar_constraint_axis,
            "mpm_planar_constraint_mode": self.mpm_planar_constraint_mode,
            "mpm_velocity_damping": float(self.mpm_velocity_damping),
        }


def _validate_optional_positive(value, name: str) -> None:
    if value is not None and float(value) <= 0.0:
        raise ValueError(f"{name} must be positive when provided")


def _path_exists(path) -> bool:
    path_obj = Path(path)
    if path_obj.is_absolute():
        return path_obj.is_file()
    return (_repo_root() / path_obj).is_file() or path_obj.is_file()


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[4]
