from dataclasses import asdict, dataclass
import json
import os
from pathlib import Path


EXPECTED_DISPLACEMENT_ROW_COUNT = 243
EXPECTED_PHASE_SAMPLE_COUNT = 81
EXPECTED_TRACKED_REGIONS = (
    "mantle_outer",
    "mantle_cavity_proxy",
    "funnel_outlet_proxy",
)

MUTATION_FLAG_FIELDS = (
    "apply_to_driver",
    "apply_to_mpm_particles",
    "apply_to_lbm_solid_phi",
    "apply_to_lbm_solid_vel",
    "apply_to_projection",
    "update_dynamic_solid",
    "recompute_boundary_links",
    "mutate_geometry_state",
)


@dataclass(frozen=True)
class GeometryMotionInterfaceConfig:
    geometry_motion_id: str
    geometry_motion_mode: str
    displacement_config_path: str
    displacement_artifact_path: str
    schedule_config_path: str
    motion_mapping_config_path: str
    region_config_path: str
    geometry_config_path: str
    application_mode: str = "diagnostic_only"
    apply_to_driver: bool = False
    apply_to_mpm_particles: bool = False
    apply_to_lbm_solid_phi: bool = False
    apply_to_lbm_solid_vel: bool = False
    apply_to_projection: bool = False
    update_dynamic_solid: bool = False
    recompute_boundary_links: bool = False
    mutate_geometry_state: bool = False
    diagnostic_only: bool = True
    deterministic: bool = True
    scope_note: str = "Step 43 geometry motion driver interface only; no geometry mutation"

    def __post_init__(self):
        for field in MUTATION_FLAG_FIELDS:
            object.__setattr__(self, field, bool(getattr(self, field)))
        object.__setattr__(self, "diagnostic_only", bool(self.diagnostic_only))
        object.__setattr__(self, "deterministic", bool(self.deterministic))

    @classmethod
    def from_json(cls, path):
        with _resolve_path(path).open("r", encoding="utf-8") as f:
            return cls(**json.load(f))

    def to_dict(self):
        return asdict(self)


def validate_geometry_motion_interface_config(config: GeometryMotionInterfaceConfig, root=None) -> list[dict]:
    root_path = _repo_root() if root is None else Path(root)
    displacement = load_displacement_artifact_summary(config, root_path)
    rows = [
        _check("geometry_motion_id_expected", config.geometry_motion_id == "step43_geometry_motion_prescribed_diagnostic_only", config.geometry_motion_id, "Step 43 geometry motion id must be stable"),
        _check("geometry_motion_mode_expected", config.geometry_motion_mode == "prescribed_kinematic", config.geometry_motion_mode, "Step 43 interface config must be prescribed_kinematic"),
        _check("application_mode_expected", config.application_mode == "diagnostic_only", config.application_mode, "Step 43 application mode must be diagnostic_only"),
        _check("diagnostic_only_true", config.diagnostic_only is True, config.diagnostic_only, "Step 43 interface must remain diagnostic-only"),
        _check("deterministic_true", config.deterministic is True, config.deterministic, "Step 43 interface must be deterministic"),
        _check("displacement_config_path_exists", _exists(root_path, config.displacement_config_path), config.displacement_config_path, "Step 42 displacement config must exist"),
        _check("displacement_artifact_path_exists", _exists(root_path, config.displacement_artifact_path), config.displacement_artifact_path, "Step 42 displacement artifact must exist"),
        _check("schedule_config_path_exists", _exists(root_path, config.schedule_config_path), config.schedule_config_path, "Step 32 schedule config must exist"),
        _check("motion_mapping_config_path_exists", _exists(root_path, config.motion_mapping_config_path), config.motion_mapping_config_path, "Step 33 motion mapping config must exist"),
        _check("region_config_path_exists", _exists(root_path, config.region_config_path), config.region_config_path, "Step 30 region config must exist"),
        _check("geometry_config_path_exists", _exists(root_path, config.geometry_config_path), config.geometry_config_path, "Step 30 geometry config must exist"),
        _check("displacement_row_count_expected", displacement["displacement_row_count"] == EXPECTED_DISPLACEMENT_ROW_COUNT, displacement["displacement_row_count"], "Step 42 displacement artifact must have 243 rows"),
        _check("phase_sample_count_expected", displacement["phase_sample_count"] == EXPECTED_PHASE_SAMPLE_COUNT, displacement["phase_sample_count"], "Step 42 displacement artifact must have 81 phases"),
        _check("tracked_regions_expected", tuple(displacement["tracked_regions"]) == EXPECTED_TRACKED_REGIONS, displacement["tracked_regions"], "tracked regions must match Step 42"),
        _check("tracked_region_count_expected", displacement["tracked_region_count"] == len(EXPECTED_TRACKED_REGIONS), displacement["tracked_region_count"], "tracked region count must be three"),
        _check("scope_note_valid", "geometry motion driver interface only" in config.scope_note and "no geometry mutation" in config.scope_note, config.scope_note, "scope_note must state interface-only and no geometry mutation"),
    ]
    for field in MUTATION_FLAG_FIELDS:
        rows.append(_check(f"{field}_false", getattr(config, field) is False, getattr(config, field), f"{field} must remain false"))
    rows.append(_check("all_mutation_flags_false", mutation_flag_enabled_count(config) == 0, mutation_flag_enabled_count(config), "all mutation flags must be false"))
    return rows


def summarize_geometry_motion_config_validation(rows: list[dict], config: GeometryMotionInterfaceConfig, root=None) -> dict:
    root_path = _repo_root() if root is None else Path(root)
    displacement = load_displacement_artifact_summary(config, root_path)
    summary = {
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if bool(row["pass"])),
        "validation_pass": all(bool(row["pass"]) for row in rows),
        "geometry_motion_mode": config.geometry_motion_mode,
        "application_mode": config.application_mode,
        "diagnostic_only": bool(config.diagnostic_only),
        "all_mutation_flags_false": mutation_flag_enabled_count(config) == 0,
    }
    summary.update(displacement)
    summary.update(mutation_flags(config))
    return summary


def load_displacement_artifact_summary(config: GeometryMotionInterfaceConfig, root=None) -> dict:
    root_path = _repo_root() if root is None else Path(root)
    payload = _read_json(_resolve_relative(root_path, config.displacement_artifact_path))
    summary = payload.get("summary", {})
    rows = payload.get("rows", [])
    tracked_regions = summary.get("tracked_regions", sorted({row.get("region_id") for row in rows}))
    return {
        "displacement_row_count": int(summary.get("row_count", len(rows))),
        "phase_sample_count": int(summary.get("phase_sample_count", len({int(row['sample_index']) for row in rows}) if rows else 0)),
        "tracked_region_count": int(summary.get("tracked_region_count", len(tracked_regions))),
        "tracked_regions": list(tracked_regions),
        "max_displacement_norm": float(summary.get("max_displacement_norm", 0.0)),
        "displacement_finite_pass": bool(summary.get("finite_pass", False)),
        "displacement_bounds_pass": bool(summary.get("bounds_pass", False)),
        "displacement_diagnostic_only_pass": bool(summary.get("diagnostic_only_pass", False)),
    }


def mutation_flags(config: GeometryMotionInterfaceConfig) -> dict:
    return {field: bool(getattr(config, field)) for field in MUTATION_FLAG_FIELDS}


def mutation_flag_enabled_count(config: GeometryMotionInterfaceConfig) -> int:
    return sum(1 for enabled in mutation_flags(config).values() if enabled)


def _check(name: str, passed: bool, value, notes: str) -> dict:
    return {"check": name, "pass": bool(passed), "value": value, "notes": notes}


def _exists(root: Path, relative_path) -> bool:
    path = _resolve_relative(root, relative_path)
    return path.is_file()


def _read_json(path):
    with Path(path).open("r", encoding="utf-8") as f:
        return json.load(f)


def _resolve_relative(root: Path, path) -> Path:
    path_obj = Path(os.fspath(path))
    if path_obj.is_absolute():
        return path_obj
    return root / path_obj


def _resolve_path(path) -> Path:
    path_obj = Path(os.fspath(path))
    if path_obj.is_absolute():
        return path_obj
    return _repo_root() / path_obj


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]
