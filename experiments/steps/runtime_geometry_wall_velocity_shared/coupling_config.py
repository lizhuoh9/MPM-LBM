from dataclasses import asdict, dataclass
import json
import math
import os
from pathlib import Path


EXPECTED_COUPLING_SMOKE_ID = "step46_runtime_geometry_wall_velocity_one_step"
EXPECTED_PHASE = 0.35
EXPECTED_N_GRID = 32
EXPECTED_N_LBM_STEPS = 1
EXPECTED_MPM_SUBSTEPS = 1
EXPECTED_COUPLING_MODE = "moving_boundary"
EXPECTED_REACTION_TRANSFER_MODE = "engineering"

MUTATION_FLAG_FIELDS = (
    "persist_displaced_geometry",
    "persist_projected_state",
    "persist_lbm_solid_vel",
    "write_displaced_particles",
    "write_dense_displacement_field",
    "write_vtk",
    "write_particles",
    "update_default_driver_geometry",
    "update_default_lbm_state",
    "update_default_mpm_state",
    "update_default_projection_state",
    "update_dynamic_solid_persistently",
    "recompute_production_boundary_links",
    "modify_moving_bounceback_formula",
)


@dataclass(frozen=True)
class RuntimeGeometryWallVelocityCouplingSmokeConfig:
    coupling_smoke_id: str
    runtime_projection_config_path: str
    diagnostic_geometry_update_config_path: str
    wall_velocity_application_config_path: str
    boundary_motion_config_path: str
    geometry_config_path: str
    region_config_path: str
    phase: float
    n_grid: int
    n_lbm_steps: int
    mpm_substeps_per_lbm_step: int
    coupling_mode: str
    reaction_transfer_mode: str
    enable_runtime_geometry_projection: bool
    enable_wall_velocity_application: bool
    persist_displaced_geometry: bool = False
    persist_projected_state: bool = False
    persist_lbm_solid_vel: bool = False
    write_displaced_particles: bool = False
    write_dense_displacement_field: bool = False
    write_vtk: bool = False
    write_particles: bool = False
    update_default_driver_geometry: bool = False
    update_default_lbm_state: bool = False
    update_default_mpm_state: bool = False
    update_default_projection_state: bool = False
    update_dynamic_solid_persistently: bool = False
    recompute_production_boundary_links: bool = False
    modify_moving_bounceback_formula: bool = False
    diagnostic_only: bool = True
    scope_note: str = "one-step opt-in runtime geometry plus wall velocity coupling smoke only"

    def __post_init__(self):
        object.__setattr__(self, "phase", float(self.phase))
        object.__setattr__(self, "n_grid", int(self.n_grid))
        object.__setattr__(self, "n_lbm_steps", int(self.n_lbm_steps))
        object.__setattr__(self, "mpm_substeps_per_lbm_step", int(self.mpm_substeps_per_lbm_step))
        object.__setattr__(self, "enable_runtime_geometry_projection", bool(self.enable_runtime_geometry_projection))
        object.__setattr__(self, "enable_wall_velocity_application", bool(self.enable_wall_velocity_application))
        for field in MUTATION_FLAG_FIELDS:
            object.__setattr__(self, field, bool(getattr(self, field)))
        object.__setattr__(self, "diagnostic_only", bool(self.diagnostic_only))

    @classmethod
    def from_json(cls, path):
        with _resolve_path(path).open("r", encoding="utf-8") as f:
            return cls(**json.load(f))

    def to_dict(self):
        return asdict(self)


def validate_coupling_smoke_config(config: RuntimeGeometryWallVelocityCouplingSmokeConfig, root=None) -> list[dict]:
    root_path = _repo_root() if root is None else Path(root)
    rows = [
        _check("coupling_smoke_id_expected", config.coupling_smoke_id == EXPECTED_COUPLING_SMOKE_ID, config.coupling_smoke_id, "Step 46 coupling smoke id must be stable"),
        _check("runtime_projection_config_path_exists", _exists(root_path, config.runtime_projection_config_path), config.runtime_projection_config_path, "Step 45 runtime projection config must exist"),
        _check("diagnostic_geometry_update_config_path_exists", _exists(root_path, config.diagnostic_geometry_update_config_path), config.diagnostic_geometry_update_config_path, "Step 44 diagnostic geometry config must exist"),
        _check("wall_velocity_application_config_path_exists", _exists(root_path, config.wall_velocity_application_config_path), config.wall_velocity_application_config_path, "Step 41 wall velocity application config must exist"),
        _check("boundary_motion_config_path_exists", _exists(root_path, config.boundary_motion_config_path), config.boundary_motion_config_path, "Step 34 boundary motion config must exist"),
        _check("geometry_config_path_exists", _exists(root_path, config.geometry_config_path), config.geometry_config_path, "Step 30 geometry config must exist"),
        _check("region_config_path_exists", _exists(root_path, config.region_config_path), config.region_config_path, "Step 30 region config must exist"),
        _check("phase_expected", math.isclose(config.phase, EXPECTED_PHASE, rel_tol=0.0, abs_tol=1.0e-12), config.phase, "Step 46 phase must be 0.35"),
        _check("n_grid_expected", config.n_grid == EXPECTED_N_GRID, config.n_grid, "Step 46 n_grid must be 32"),
        _check("n_lbm_steps_expected", config.n_lbm_steps == EXPECTED_N_LBM_STEPS, config.n_lbm_steps, "Step 46 must use one LBM step"),
        _check("mpm_substeps_expected", config.mpm_substeps_per_lbm_step == EXPECTED_MPM_SUBSTEPS, config.mpm_substeps_per_lbm_step, "Step 46 must use one MPM substep"),
        _check("coupling_mode_expected", config.coupling_mode == EXPECTED_COUPLING_MODE, config.coupling_mode, "Step 46 coupling mode must be moving_boundary"),
        _check("reaction_transfer_mode_expected", config.reaction_transfer_mode == EXPECTED_REACTION_TRANSFER_MODE, config.reaction_transfer_mode, "Step 46 transfer mode must be engineering"),
        _check("enable_runtime_geometry_projection_true", config.enable_runtime_geometry_projection is True, config.enable_runtime_geometry_projection, "umbrella config must enable runtime geometry projection for the matrix"),
        _check("enable_wall_velocity_application_true", config.enable_wall_velocity_application is True, config.enable_wall_velocity_application, "umbrella config must enable wall velocity application for the matrix"),
        _check("diagnostic_only_true", config.diagnostic_only is True, config.diagnostic_only, "Step 46 must remain diagnostic-only"),
        _check("scope_note_valid", "one-step opt-in" in config.scope_note and "wall velocity" in config.scope_note, config.scope_note, "scope note must state one-step opt-in wall-velocity scope"),
    ]
    for field in MUTATION_FLAG_FIELDS:
        rows.append(_check(f"{field}_false", getattr(config, field) is False, getattr(config, field), f"{field} must remain false"))
    rows.append(_check("all_mutation_flags_false", mutation_flag_enabled_count(config) == 0, mutation_flag_enabled_count(config), "all mutation/write/formula flags must be false"))
    return rows


def summarize_coupling_smoke_config_validation(rows: list[dict], config: RuntimeGeometryWallVelocityCouplingSmokeConfig) -> dict:
    return {
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if bool(row["pass"])),
        "validation_pass": all(bool(row["pass"]) for row in rows),
        "coupling_smoke_id": config.coupling_smoke_id,
        "phase": config.phase,
        "n_grid": config.n_grid,
        "n_lbm_steps": config.n_lbm_steps,
        "mpm_substeps_per_lbm_step": config.mpm_substeps_per_lbm_step,
        "coupling_mode": config.coupling_mode,
        "reaction_transfer_mode": config.reaction_transfer_mode,
        "enable_runtime_geometry_projection": config.enable_runtime_geometry_projection,
        "enable_wall_velocity_application": config.enable_wall_velocity_application,
        "diagnostic_only": config.diagnostic_only,
        "all_mutation_flags_false": mutation_flag_enabled_count(config) == 0,
        **mutation_flags(config),
    }


def mutation_flags(config: RuntimeGeometryWallVelocityCouplingSmokeConfig) -> dict:
    return {field: bool(getattr(config, field)) for field in MUTATION_FLAG_FIELDS}


def mutation_flag_enabled_count(config: RuntimeGeometryWallVelocityCouplingSmokeConfig) -> int:
    return sum(1 for value in mutation_flags(config).values() if value)


def _check(name: str, passed: bool, value, notes: str) -> dict:
    return {"check": name, "pass": bool(passed), "value": value, "notes": notes}


def _exists(root: Path, relative_path) -> bool:
    path = Path(os.fspath(relative_path))
    if not path.is_absolute():
        path = root / path
    return path.is_file()


def _resolve_path(path) -> Path:
    path_obj = Path(os.fspath(path))
    if path_obj.is_absolute():
        return path_obj
    return _repo_root() / path_obj


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]
