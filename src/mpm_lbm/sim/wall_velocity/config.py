from dataclasses import asdict, dataclass
import json
import math
import os
from pathlib import Path


REQUIRED_WALL_VELOCITY_REGIONS = (
    "mantle_outer",
    "mantle_cavity_proxy",
    "funnel_outlet_proxy",
)
EXPECTED_WALL_VELOCITY_GRID_SIZES = (32, 48, 64)
EXPECTED_WALL_VELOCITY_PHASES = (0.0, 0.1, 0.2, 0.35, 0.5, 0.75, 1.0)
EXPECTED_WALL_VELOCITY_ROW_COUNT = (
    len(EXPECTED_WALL_VELOCITY_GRID_SIZES)
    * len(EXPECTED_WALL_VELOCITY_PHASES)
    * len(REQUIRED_WALL_VELOCITY_REGIONS)
)

STEP35_EXECUTION_FLAG_FIELDS = (
    "write_dense_field",
    "write_sparse_samples",
    "apply_to_lbm",
    "lbm_population_update_enabled",
    "moving_bounceback_update_enabled",
    "driver_integration_enabled",
    "jet_model_enabled",
    "actuation_enabled",
)


@dataclass(frozen=True)
class WallVelocityFieldConfig:
    velocity_field_id: str
    boundary_motion_config_path: str
    motion_mapping_config_path: str
    schedule_config_path: str
    region_config_path: str
    geometry_config_path: str
    grid_sizes: tuple[int, ...]
    phase_samples: tuple[float, ...]
    tracked_regions: tuple[str, ...]
    wall_velocity_model: str
    funnel_axis: str
    max_velocity_norm_allowed: float
    write_dense_field: bool = False
    write_sparse_samples: bool = False
    apply_to_lbm: bool = False
    lbm_population_update_enabled: bool = False
    moving_bounceback_update_enabled: bool = False
    driver_integration_enabled: bool = False
    jet_model_enabled: bool = False
    actuation_enabled: bool = False
    deterministic: bool = True
    scope_note: str = "velocity field diagnostics only; no LBM population update"

    def __post_init__(self):
        object.__setattr__(self, "grid_sizes", tuple(int(value) for value in self.grid_sizes))
        object.__setattr__(self, "phase_samples", tuple(float(value) for value in self.phase_samples))
        object.__setattr__(self, "tracked_regions", tuple(str(value) for value in self.tracked_regions))
        object.__setattr__(self, "max_velocity_norm_allowed", float(self.max_velocity_norm_allowed))
        object.__setattr__(self, "deterministic", bool(self.deterministic))
        for field in STEP35_EXECUTION_FLAG_FIELDS:
            object.__setattr__(self, field, bool(getattr(self, field)))

    @classmethod
    def from_json(cls, path):
        with _resolve_path(path).open("r", encoding="utf-8") as f:
            return cls(**json.load(f))

    def to_dict(self):
        payload = asdict(self)
        payload["grid_sizes"] = list(self.grid_sizes)
        payload["phase_samples"] = list(self.phase_samples)
        payload["tracked_regions"] = list(self.tracked_regions)
        return payload


def validate_wall_velocity_config(config: WallVelocityFieldConfig, root=None) -> list[dict]:
    root_path = _repo_root() if root is None else Path(root)
    rows = [
        _check("velocity_field_id_present", bool(config.velocity_field_id), config.velocity_field_id, "velocity_field_id must be nonempty"),
        _check(
            "boundary_motion_config_path_exists",
            _exists(root_path, config.boundary_motion_config_path),
            config.boundary_motion_config_path,
            "Step 34 boundary-motion config must exist",
        ),
        _check(
            "motion_mapping_config_path_exists",
            _exists(root_path, config.motion_mapping_config_path),
            config.motion_mapping_config_path,
            "Step 33 motion mapping config must exist",
        ),
        _check("schedule_config_path_exists", _exists(root_path, config.schedule_config_path), config.schedule_config_path, "Step 32 schedule config must exist"),
        _check("region_config_path_exists", _exists(root_path, config.region_config_path), config.region_config_path, "Step 30 region config must exist"),
        _check("geometry_config_path_exists", _exists(root_path, config.geometry_config_path), config.geometry_config_path, "Step 30 geometry config must exist"),
        _check("grid_sizes_positive", all(value > 0 for value in config.grid_sizes), list(config.grid_sizes), "grid sizes must be positive"),
        _check("grid_sizes_expected", config.grid_sizes == EXPECTED_WALL_VELOCITY_GRID_SIZES, list(config.grid_sizes), "grid sizes must be [32, 48, 64]"),
        _check(
            "phase_samples_finite",
            all(math.isfinite(value) for value in config.phase_samples),
            list(config.phase_samples),
            "phase samples must be finite",
        ),
        _check(
            "phase_samples_in_unit_interval",
            all(0.0 <= value <= 1.0 for value in config.phase_samples),
            list(config.phase_samples),
            "phase samples must be in [0, 1]",
        ),
        _check(
            "phase_samples_expected",
            _float_tuple_close(config.phase_samples, EXPECTED_WALL_VELOCITY_PHASES),
            list(config.phase_samples),
            "phase samples must match Step 35 contract",
        ),
        _check(
            "tracked_regions_include_mantle_outer",
            "mantle_outer" in config.tracked_regions,
            list(config.tracked_regions),
            "mantle_outer must be tracked",
        ),
        _check(
            "tracked_regions_include_mantle_cavity_proxy",
            "mantle_cavity_proxy" in config.tracked_regions,
            list(config.tracked_regions),
            "mantle_cavity_proxy must be tracked",
        ),
        _check(
            "tracked_regions_include_funnel_outlet_proxy",
            "funnel_outlet_proxy" in config.tracked_regions,
            list(config.tracked_regions),
            "funnel_outlet_proxy must be tracked",
        ),
        _check("tracked_regions_expected", config.tracked_regions == REQUIRED_WALL_VELOCITY_REGIONS, list(config.tracked_regions), "tracked regions must match Step 35 contract"),
        _check("wall_velocity_model_valid", config.wall_velocity_model == "diagnostic_proxy", config.wall_velocity_model, "wall_velocity_model must be diagnostic_proxy"),
        _check("funnel_axis_valid", config.funnel_axis == "+y", config.funnel_axis, "funnel_axis must be +y"),
        _check(
            "max_velocity_norm_allowed_valid",
            math.isfinite(config.max_velocity_norm_allowed) and config.max_velocity_norm_allowed > 0.0,
            config.max_velocity_norm_allowed,
            "max_velocity_norm_allowed must be finite and positive",
        ),
        _check("deterministic_enabled", config.deterministic is True, config.deterministic, "Step 35 generation must be deterministic"),
        _check(
            "scope_note_valid",
            "velocity field diagnostics only" in config.scope_note and "no LBM population update" in config.scope_note,
            config.scope_note,
            "scope_note must state diagnostics-only and no LBM population update",
        ),
    ]
    for field in STEP35_EXECUTION_FLAG_FIELDS:
        rows.append(_check(f"{field}_false", getattr(config, field) is False, getattr(config, field), f"{field} must be false"))
    rows.append(
        _check(
            "all_execution_flags_false",
            step35_execution_flag_enabled_count(config) == 0,
            step35_execution_flag_enabled_count(config),
            "all Step 35 execution flags must be disabled",
        )
    )
    return rows


def assert_valid_wall_velocity_config(config: WallVelocityFieldConfig, root=None) -> None:
    rows = validate_wall_velocity_config(config, root=root)
    summary = summarize_wall_velocity_config_validation(rows, config=config)
    if not bool(summary["validation_pass"]):
        failed = [row for row in rows if not row["pass"]]
        raise ValueError(f"Step 35 wall velocity config validation failed: {failed}")


def summarize_wall_velocity_config_validation(rows: list[dict], config: WallVelocityFieldConfig | None = None) -> dict:
    summary = {
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if bool(row["pass"])),
        "validation_pass": all(bool(row["pass"]) for row in rows),
    }
    if config is not None:
        summary.update(
            {
                "velocity_field_id": config.velocity_field_id,
                "grid_size_count": len(config.grid_sizes),
                "phase_sample_count": len(config.phase_samples),
                "tracked_region_count": len(config.tracked_regions),
                "expected_wall_velocity_row_count": EXPECTED_WALL_VELOCITY_ROW_COUNT,
                "write_dense_field": bool(config.write_dense_field),
                "write_sparse_samples": bool(config.write_sparse_samples),
                "apply_to_lbm": bool(config.apply_to_lbm),
                "lbm_population_update_enabled": bool(config.lbm_population_update_enabled),
                "moving_bounceback_update_enabled": bool(config.moving_bounceback_update_enabled),
                "driver_integration_enabled": bool(config.driver_integration_enabled),
                "jet_model_enabled": bool(config.jet_model_enabled),
                "actuation_enabled": bool(config.actuation_enabled),
                "execution_flag_enabled_count": step35_execution_flag_enabled_count(config),
            }
        )
    return summary


def step35_execution_flags(config: WallVelocityFieldConfig) -> dict:
    return {field: bool(getattr(config, field)) for field in STEP35_EXECUTION_FLAG_FIELDS}


def step35_execution_flag_enabled_count(config: WallVelocityFieldConfig) -> int:
    return sum(1 for enabled in step35_execution_flags(config).values() if enabled)


def _check(name: str, passed: bool, value, notes: str) -> dict:
    return {"check": name, "pass": bool(passed), "value": value, "notes": notes}


def _exists(root: Path, relative_path: str) -> bool:
    path = Path(os.fspath(relative_path))
    if not path.is_absolute():
        path = root / path
    return path.is_file()


def _float_tuple_close(left, right, tolerance=1.0e-12) -> bool:
    if len(left) != len(right):
        return False
    return all(abs(float(a) - float(b)) <= tolerance for a, b in zip(left, right))


def _resolve_path(path) -> Path:
    path_obj = Path(os.fspath(path))
    if path_obj.is_absolute():
        return path_obj
    return _repo_root() / path_obj


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]
