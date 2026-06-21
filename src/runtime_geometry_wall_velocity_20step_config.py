from dataclasses import asdict, dataclass
import json
import math
import os
from pathlib import Path


EXPECTED_ENVELOPE_ID = "step49_runtime_geometry_wall_velocity_20step_envelope"
EXPECTED_PHASE_SEQUENCE = (0.0, 0.025, 0.05, 0.075, 0.1, 0.125, 0.15, 0.175, 0.2, 0.225, 0.25, 0.275, 0.3, 0.325, 0.35, 0.375, 0.4, 0.425, 0.45, 0.5)
EXPECTED_N_GRID = 32
EXPECTED_N_LBM_STEPS = 20
EXPECTED_MPM_SUBSTEPS = 5
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
class RuntimeGeometryWallVelocityTwentyStepEnvelopeConfig:
    twenty_step_envelope_id: str
    base_step48_config_path: str
    runtime_projection_config_path: str
    diagnostic_geometry_update_config_path: str
    wall_velocity_application_config_path: str
    boundary_motion_config_path: str
    geometry_config_path: str
    region_config_path: str
    n_grid: int
    n_lbm_steps: int
    mpm_substeps_per_lbm_step: int
    phase_sequence: tuple[float, ...]
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
    scope_note: str = "32^3 twenty-step engineering-only runtime geometry plus wall velocity envelope; not a full-cycle run"

    def __post_init__(self):
        object.__setattr__(self, "n_grid", int(self.n_grid))
        object.__setattr__(self, "n_lbm_steps", int(self.n_lbm_steps))
        object.__setattr__(self, "mpm_substeps_per_lbm_step", int(self.mpm_substeps_per_lbm_step))
        object.__setattr__(self, "phase_sequence", tuple(float(value) for value in self.phase_sequence))
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
        data = asdict(self)
        data["phase_sequence"] = list(self.phase_sequence)
        return data


def validate_twenty_step_envelope_config(config: RuntimeGeometryWallVelocityTwentyStepEnvelopeConfig, root=None) -> list[dict]:
    root_path = _repo_root() if root is None else Path(root)
    rows = [
        _check("twenty_step_envelope_id_expected", config.twenty_step_envelope_id == EXPECTED_ENVELOPE_ID, config.twenty_step_envelope_id, "Step 49 envelope id must be stable"),
        _check("base_step48_config_path_exists", _exists(root_path, config.base_step48_config_path), config.base_step48_config_path, "Step 48 envelope config must exist"),
        _check("runtime_projection_config_path_exists", _exists(root_path, config.runtime_projection_config_path), config.runtime_projection_config_path, "Step 45 runtime projection config must exist"),
        _check("diagnostic_geometry_update_config_path_exists", _exists(root_path, config.diagnostic_geometry_update_config_path), config.diagnostic_geometry_update_config_path, "Step 44 diagnostic geometry config must exist"),
        _check("wall_velocity_application_config_path_exists", _exists(root_path, config.wall_velocity_application_config_path), config.wall_velocity_application_config_path, "Step 41 wall velocity application config must exist"),
        _check("boundary_motion_config_path_exists", _exists(root_path, config.boundary_motion_config_path), config.boundary_motion_config_path, "Step 34 boundary motion config must exist"),
        _check("geometry_config_path_exists", _exists(root_path, config.geometry_config_path), config.geometry_config_path, "Step 30 geometry config must exist"),
        _check("region_config_path_exists", _exists(root_path, config.region_config_path), config.region_config_path, "Step 30 region config must exist"),
        _check("n_grid_expected", config.n_grid == EXPECTED_N_GRID, config.n_grid, "Step 49 n_grid must be 32"),
        _check("n_lbm_steps_expected", config.n_lbm_steps == EXPECTED_N_LBM_STEPS, config.n_lbm_steps, "Step 49 must use twenty LBM steps"),
        _check("mpm_substeps_expected", config.mpm_substeps_per_lbm_step == EXPECTED_MPM_SUBSTEPS, config.mpm_substeps_per_lbm_step, "Step 49 must use five MPM substeps per LBM step"),
        _check("phase_sequence_expected", _same_phase_sequence(config.phase_sequence, EXPECTED_PHASE_SEQUENCE), list(config.phase_sequence), "Step 49 phase sequence must match the twenty-step envelope"),
        _check("phase_count_expected", len(config.phase_sequence) == 20, len(config.phase_sequence), "Step 49 must use twenty phases"),
        _check("phase_sequence_finite", all(math.isfinite(float(value)) for value in config.phase_sequence), list(config.phase_sequence), "all phases must be finite"),
        _check("phase_sequence_bounds", all(0.0 <= float(value) <= 1.0 for value in config.phase_sequence), list(config.phase_sequence), "all phases must be in [0, 1]"),
        _check("phase_sequence_nondecreasing", _nondecreasing(config.phase_sequence), list(config.phase_sequence), "phases must be nondecreasing"),
        _check("phase_starts_at_0", math.isclose(config.phase_sequence[0], 0.0, rel_tol=0.0, abs_tol=1.0e-12), config.phase_sequence[0], "Step 49 phase sequence must start at 0.0"),
        _check("phase_contains_035", any(math.isclose(value, 0.35, rel_tol=0.0, abs_tol=1.0e-12) for value in config.phase_sequence), list(config.phase_sequence), "Step 49 phase sequence must include 0.35"),
        _check("phase_ends_at_05", math.isclose(config.phase_sequence[-1], 0.5, rel_tol=0.0, abs_tol=1.0e-12), config.phase_sequence[-1], "Step 49 phase sequence must end at 0.5"),
        _check("coupling_mode_expected", config.coupling_mode == EXPECTED_COUPLING_MODE, config.coupling_mode, "Step 49 coupling mode must be moving_boundary"),
        _check("reaction_transfer_mode_expected", config.reaction_transfer_mode == EXPECTED_REACTION_TRANSFER_MODE, config.reaction_transfer_mode, "Step 49 transfer mode must be engineering"),
        _check("enable_runtime_geometry_projection_true", config.enable_runtime_geometry_projection is True, config.enable_runtime_geometry_projection, "umbrella config must enable runtime geometry projection"),
        _check("enable_wall_velocity_application_true", config.enable_wall_velocity_application is True, config.enable_wall_velocity_application, "umbrella config must enable wall velocity application"),
        _check("diagnostic_only_true", config.diagnostic_only is True, config.diagnostic_only, "Step 49 must remain diagnostic-only"),
        _check("scope_note_valid", "twenty-step" in config.scope_note and "engineering-only" in config.scope_note and "full-cycle" in config.scope_note, config.scope_note, "scope note must state twenty-step engineering-only non-full-cycle scope"),
    ]
    for field in MUTATION_FLAG_FIELDS:
        rows.append(_check(f"{field}_false", getattr(config, field) is False, getattr(config, field), f"{field} must remain false"))
    rows.append(_check("all_mutation_flags_false", mutation_flag_enabled_count(config) == 0, mutation_flag_enabled_count(config), "all mutation/write/formula flags must be false"))
    return rows


def summarize_twenty_step_envelope_config_validation(rows: list[dict], config: RuntimeGeometryWallVelocityTwentyStepEnvelopeConfig) -> dict:
    return {
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if bool(row["pass"])),
        "validation_pass": all(bool(row["pass"]) for row in rows),
        "twenty_step_envelope_id": config.twenty_step_envelope_id,
        "n_grid": config.n_grid,
        "n_lbm_steps": config.n_lbm_steps,
        "mpm_substeps_per_lbm_step": config.mpm_substeps_per_lbm_step,
        "phase_count": len(config.phase_sequence),
        "phase_sequence": list(config.phase_sequence),
        "phase_contains_035": any(math.isclose(value, 0.35, rel_tol=0.0, abs_tol=1.0e-12) for value in config.phase_sequence),
        "phase_ends_at_05": math.isclose(config.phase_sequence[-1], 0.5, rel_tol=0.0, abs_tol=1.0e-12),
        "phase_nondecreasing": _nondecreasing(config.phase_sequence),
        "coupling_mode": config.coupling_mode,
        "reaction_transfer_mode": config.reaction_transfer_mode,
        "enable_runtime_geometry_projection": config.enable_runtime_geometry_projection,
        "enable_wall_velocity_application": config.enable_wall_velocity_application,
        "diagnostic_only": config.diagnostic_only,
        "all_mutation_flags_false": mutation_flag_enabled_count(config) == 0,
        **mutation_flags(config),
    }


def mutation_flags(config: RuntimeGeometryWallVelocityTwentyStepEnvelopeConfig) -> dict:
    return {field: bool(getattr(config, field)) for field in MUTATION_FLAG_FIELDS}


def mutation_flag_enabled_count(config: RuntimeGeometryWallVelocityTwentyStepEnvelopeConfig) -> int:
    return sum(1 for value in mutation_flags(config).values() if value)


def _same_phase_sequence(left, right) -> bool:
    return len(left) == len(right) and all(math.isclose(float(a), float(b), rel_tol=0.0, abs_tol=1.0e-12) for a, b in zip(left, right))


def _nondecreasing(values) -> bool:
    return all(float(right) >= float(left) for left, right in zip(values, values[1:]))


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
