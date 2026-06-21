from dataclasses import asdict, dataclass
import json
import math
import os
from pathlib import Path


EXPECTED_PROJECTION_INTEGRATION_ID = "step45_runtime_geometry_projection_integration_smoke"
EXPECTED_INTEGRATION_MODE = "transient_projection_only"
EXPECTED_SELECTED_PHASES = (0.0, 0.2, 0.35, 0.5, 1.0)
EXPECTED_GRID_SIZES = (32, 48)
EXPECTED_TRACKED_REGIONS = (
    "mantle_outer",
    "mantle_cavity_proxy",
    "funnel_outlet_proxy",
)

MUTATION_FLAG_FIELDS = (
    "persist_projected_state",
    "persist_displaced_geometry",
    "write_displaced_particles",
    "write_dense_displacement_field",
    "write_vtk",
    "apply_to_driver_state",
    "apply_to_default_lbm_state",
    "apply_to_default_mpm_state",
    "apply_to_default_projection_state",
    "update_dynamic_solid",
    "recompute_production_boundary_links",
    "mutate_original_geometry",
)


@dataclass(frozen=True)
class RuntimeGeometryProjectionIntegrationConfig:
    projection_integration_id: str
    diagnostic_geometry_update_config_path: str
    geometry_motion_interface_config_path: str
    displacement_artifact_path: str
    geometry_config_path: str
    region_config_path: str
    step44_projection_artifact_path: str
    selected_phases: tuple[float, ...]
    grid_sizes: tuple[int, ...]
    tracked_regions: tuple[str, ...]
    integration_mode: str
    persist_projected_state: bool = False
    persist_displaced_geometry: bool = False
    write_displaced_particles: bool = False
    write_dense_displacement_field: bool = False
    write_vtk: bool = False
    apply_to_driver_state: bool = False
    apply_to_default_lbm_state: bool = False
    apply_to_default_mpm_state: bool = False
    apply_to_default_projection_state: bool = False
    update_dynamic_solid: bool = False
    recompute_production_boundary_links: bool = False
    mutate_original_geometry: bool = False
    diagnostic_only: bool = True
    deterministic: bool = True
    scope_note: str = "transient projection integration smoke only; no persistent moving-geometry coupling"

    def __post_init__(self):
        object.__setattr__(self, "selected_phases", tuple(float(value) for value in self.selected_phases))
        object.__setattr__(self, "grid_sizes", tuple(int(value) for value in self.grid_sizes))
        object.__setattr__(self, "tracked_regions", tuple(str(value) for value in self.tracked_regions))
        for field in MUTATION_FLAG_FIELDS:
            object.__setattr__(self, field, bool(getattr(self, field)))
        object.__setattr__(self, "diagnostic_only", bool(self.diagnostic_only))
        object.__setattr__(self, "deterministic", bool(self.deterministic))

    @classmethod
    def from_json(cls, path):
        with _resolve_path(path).open("r", encoding="utf-8") as f:
            return cls(**json.load(f))

    def to_dict(self):
        payload = asdict(self)
        payload["selected_phases"] = list(self.selected_phases)
        payload["grid_sizes"] = list(self.grid_sizes)
        payload["tracked_regions"] = list(self.tracked_regions)
        return payload


def validate_runtime_geometry_projection_config(config: RuntimeGeometryProjectionIntegrationConfig, root=None) -> list[dict]:
    root_path = _repo_root() if root is None else Path(root)
    rows = [
        _check("projection_integration_id_expected", config.projection_integration_id == EXPECTED_PROJECTION_INTEGRATION_ID, config.projection_integration_id, "Step 45 projection integration id must be stable"),
        _check("integration_mode_expected", config.integration_mode == EXPECTED_INTEGRATION_MODE, config.integration_mode, "Step 45 integration mode must be transient_projection_only"),
        _check("diagnostic_only_true", config.diagnostic_only is True, config.diagnostic_only, "Step 45 must remain diagnostic-only"),
        _check("deterministic_true", config.deterministic is True, config.deterministic, "Step 45 must remain deterministic"),
        _check("diagnostic_geometry_update_config_path_exists", _exists(root_path, config.diagnostic_geometry_update_config_path), config.diagnostic_geometry_update_config_path, "Step 44 diagnostic update config must exist"),
        _check("geometry_motion_interface_config_path_exists", _exists(root_path, config.geometry_motion_interface_config_path), config.geometry_motion_interface_config_path, "Step 43 geometry-motion interface config must exist"),
        _check("displacement_artifact_path_exists", _exists(root_path, config.displacement_artifact_path), config.displacement_artifact_path, "Step 42 displacement artifact must exist"),
        _check("geometry_config_path_exists", _exists(root_path, config.geometry_config_path), config.geometry_config_path, "Step 30 geometry config must exist"),
        _check("region_config_path_exists", _exists(root_path, config.region_config_path), config.region_config_path, "Step 30 region config must exist"),
        _check("step44_projection_artifact_path_exists", _exists(root_path, config.step44_projection_artifact_path), config.step44_projection_artifact_path, "Step 44 projection-only smoke artifact must exist"),
        _check("selected_phases_expected", _float_tuple_equal(config.selected_phases, EXPECTED_SELECTED_PHASES), list(config.selected_phases), "selected phases must match Step 45 contract"),
        _check("selected_phases_bounded", all(0.0 <= phase <= 1.0 for phase in config.selected_phases), list(config.selected_phases), "selected phases must be in [0, 1]"),
        _check("grid_sizes_expected", config.grid_sizes == EXPECTED_GRID_SIZES, list(config.grid_sizes), "grid sizes must be [32, 48]"),
        _check("grid_sizes_positive", all(grid > 0 for grid in config.grid_sizes), list(config.grid_sizes), "grid sizes must be positive"),
        _check("tracked_regions_expected", config.tracked_regions == EXPECTED_TRACKED_REGIONS, list(config.tracked_regions), "tracked regions must match Step 44"),
        _check("scope_note_valid", "transient projection integration smoke" in config.scope_note and "no persistent" in config.scope_note, config.scope_note, "scope note must state transient no-persistent scope"),
    ]
    for field in MUTATION_FLAG_FIELDS:
        rows.append(_check(f"{field}_false", getattr(config, field) is False, getattr(config, field), f"{field} must remain false"))
    rows.append(_check("all_mutation_flags_false", mutation_flag_enabled_count(config) == 0, mutation_flag_enabled_count(config), "all mutation flags must be false"))
    return rows


def summarize_runtime_geometry_projection_config_validation(rows: list[dict], config: RuntimeGeometryProjectionIntegrationConfig) -> dict:
    return {
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if bool(row["pass"])),
        "validation_pass": all(bool(row["pass"]) for row in rows),
        "projection_integration_id": config.projection_integration_id,
        "integration_mode": config.integration_mode,
        "selected_phase_count": len(config.selected_phases),
        "selected_phases": list(config.selected_phases),
        "grid_sizes": list(config.grid_sizes),
        "tracked_region_count": len(config.tracked_regions),
        "tracked_regions": list(config.tracked_regions),
        "diagnostic_only": bool(config.diagnostic_only),
        "deterministic": bool(config.deterministic),
        "all_mutation_flags_false": mutation_flag_enabled_count(config) == 0,
        **mutation_flags(config),
    }


def mutation_flags(config: RuntimeGeometryProjectionIntegrationConfig) -> dict:
    return {field: bool(getattr(config, field)) for field in MUTATION_FLAG_FIELDS}


def mutation_flag_enabled_count(config: RuntimeGeometryProjectionIntegrationConfig) -> int:
    return sum(1 for value in mutation_flags(config).values() if value)


def _check(name: str, passed: bool, value, notes: str) -> dict:
    return {"check": name, "pass": bool(passed), "value": value, "notes": notes}


def _exists(root: Path, relative_path) -> bool:
    path = Path(os.fspath(relative_path))
    if not path.is_absolute():
        path = root / path
    return path.is_file()


def _float_tuple_equal(left, right, tol=1.0e-12) -> bool:
    return len(left) == len(right) and all(math.isclose(float(a), float(b), rel_tol=0.0, abs_tol=tol) for a, b in zip(left, right))


def _resolve_path(path) -> Path:
    path_obj = Path(os.fspath(path))
    if path_obj.is_absolute():
        return path_obj
    return _repo_root() / path_obj


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]
