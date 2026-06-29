from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class OfficialTutorialSetup:
    duct_length_m: float
    duct_height_m: float
    flap_height_m: float
    flap_thickness_m: float
    half_domain_mode: bool
    inlet_air_velocity_mps: float
    outlet_type: str
    monitor_point_m: list[float]
    monitor_quantity: str
    official_tutorial_time_steps: int
    official_tutorial_dt_s: float
    official_tutorial_total_time_s: float
    max_iterations_per_time_step: int


@dataclass(frozen=True)
class OfficialMaterial:
    material_name: str
    solid_density_kg_m3: float
    youngs_modulus_pa: float
    poisson_ratio: float


@dataclass(frozen=True)
class SolverGrid:
    nx: int
    ny: int
    nz: int


@dataclass(frozen=True)
class SolverGeometryMapping:
    solver_domain_normalized: dict[str, list[float]]
    duct_normalized: dict[str, list[float]]
    flap_normalized: dict[str, Any]
    physical_to_normalized_mapping: dict[str, str]
    geometry_equivalence_claim_allowed: bool


@dataclass(frozen=True)
class BoundaryConditionSpec:
    inlet: str
    inlet_velocity_mps: float
    outlet: str
    wall: str
    flap_wall: str
    z_boundary_proxy: str


@dataclass(frozen=True)
class FSIInterfaceSpec:
    interface_connectivity: str
    solid_interface: str
    fluid_interface: str
    fixed_base_policy: str
    moving_wall_semantics: str
    fluent_intrinsic_fsi_equivalence_claim_allowed: bool


@dataclass(frozen=True)
class MonitorSpec:
    monitor_point_m: list[float]
    monitor_point_normalized: list[float]
    monitor_index: list[int]
    monitor_quantity: str
    nearest_cell_policy: str


@dataclass(frozen=True)
class DimensionlessMapping:
    duct_length_m: float
    duct_height_m: float
    solver_nx: int
    solver_ny: int
    solver_nz: int
    dx_m_if_x_length_controls: float
    dy_m_if_duct_height_controls: float | None
    inlet_velocity_mps: float
    official_dt_s: float
    official_total_time_s: float
    official_time_steps: int
    mapping_scope: str
    direct_physical_reynolds_validation_allowed: bool
    physical_reynolds_parity_claim_allowed: bool
    tau_margin_validation_required_before_physical_re_claim: bool


@dataclass(frozen=True)
class PostprocessSpec:
    expected_outputs: dict[str, str]
    validation_claim_allowed: bool
    step156_required_before_velocity_plots: bool


@dataclass(frozen=True)
class CompiledOfficialDuctFlapCase:
    step: int
    status: str
    case_name: str
    case_version: int
    source_step: int
    source_step153_root: str
    source_step153_status: str
    official_tutorial_setup: dict[str, Any]
    official_material: dict[str, Any]
    solver_grid: dict[str, int]
    solver_geometry_mapping: dict[str, Any]
    boundary_condition_spec: dict[str, Any]
    fsi_interface_spec: dict[str, Any]
    monitor_spec: dict[str, Any]
    dimensionless_mapping: dict[str, Any]
    lbm_boundary_semantics_required_for_step155: dict[str, Any]
    mask_artifacts: dict[str, str]
    postprocess_spec_path: str
    official_mesh_imported: bool
    official_fluent_files_used_as_runtime_input: bool
    validation_claim_allowed: bool
    figure_29_3_parity_claim_allowed: bool
    selected96_execution_allowed: bool


def to_json_dict(value: Any) -> Any:
    if hasattr(value, "__dataclass_fields__"):
        return to_json_dict(asdict(value))
    if isinstance(value, dict):
        return {str(key): to_json_dict(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [to_json_dict(item) for item in value]
    return value
