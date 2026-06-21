from dataclasses import asdict, dataclass
import json
import os
from pathlib import Path
from typing import Optional


EXPECTED_SCHEDULE_ROW_COUNT = 81
EXPECTED_MOTION_ROW_COUNT = 243
EXPECTED_TRACKED_REGION_COUNT = 3


EXECUTION_FLAG_FIELDS = (
    "driver_integration_enabled",
    "lbm_wall_velocity_enabled",
    "lbm_population_update_enabled",
    "mpm_grid_velocity_enabled",
    "projector_integration_enabled",
    "coupling_integration_enabled",
    "moving_bounceback_update_enabled",
    "jet_model_enabled",
    "actuation_enabled",
)


@dataclass(frozen=True)
class BoundaryMotionInterfaceConfig:
    interface_id: str
    schedule_config_path: str
    motion_mapping_config_path: str
    schedule_output_path: Optional[str] = "outputs/step32_kinematics_schedule/kinematics_schedule.json"
    motion_mapping_output_path: Optional[str] = "outputs/step33_motion_mapping/motion_mapping.json"
    expected_schedule_row_count: int = EXPECTED_SCHEDULE_ROW_COUNT
    expected_motion_row_count: int = EXPECTED_MOTION_ROW_COUNT
    expected_tracked_region_count: int = EXPECTED_TRACKED_REGION_COUNT
    diagnostic_only: bool = True
    driver_integration_enabled: bool = False
    lbm_wall_velocity_enabled: bool = False
    lbm_population_update_enabled: bool = False
    mpm_grid_velocity_enabled: bool = False
    projector_integration_enabled: bool = False
    coupling_integration_enabled: bool = False
    moving_bounceback_update_enabled: bool = False
    jet_model_enabled: bool = False
    actuation_enabled: bool = False
    deterministic: bool = True
    scope_note: str = "Step 34 diagnostic-only boundary-motion interface; no-op driver report"

    def __post_init__(self):
        object.__setattr__(self, "expected_schedule_row_count", int(self.expected_schedule_row_count))
        object.__setattr__(self, "expected_motion_row_count", int(self.expected_motion_row_count))
        object.__setattr__(self, "expected_tracked_region_count", int(self.expected_tracked_region_count))
        object.__setattr__(self, "diagnostic_only", bool(self.diagnostic_only))
        object.__setattr__(self, "deterministic", bool(self.deterministic))
        for field in EXECUTION_FLAG_FIELDS:
            object.__setattr__(self, field, bool(getattr(self, field)))

    @classmethod
    def from_json(cls, path):
        with _resolve_path(path).open("r", encoding="utf-8") as f:
            return cls(**json.load(f))

    def to_dict(self):
        return asdict(self)


def validate_boundary_motion_interface_config(config: BoundaryMotionInterfaceConfig, root=None) -> list[dict]:
    root_path = _repo_root() if root is None else Path(root)
    rows = [
        _check("interface_id_present", bool(config.interface_id), config.interface_id, "interface_id must be nonempty"),
        _check(
            "schedule_config_path_exists",
            _exists(root_path, config.schedule_config_path),
            config.schedule_config_path,
            "Step 32 schedule config must exist",
        ),
        _check(
            "motion_mapping_config_path_exists",
            _exists(root_path, config.motion_mapping_config_path),
            config.motion_mapping_config_path,
            "Step 33 motion mapping config must exist",
        ),
        _check(
            "schedule_output_path_exists",
            config.schedule_output_path is None or _exists(root_path, config.schedule_output_path),
            config.schedule_output_path,
            "accepted Step 32 schedule output must exist when configured",
        ),
        _check(
            "motion_mapping_output_path_exists",
            config.motion_mapping_output_path is None or _exists(root_path, config.motion_mapping_output_path),
            config.motion_mapping_output_path,
            "accepted Step 33 motion mapping output must exist when configured",
        ),
        _check(
            "expected_schedule_row_count",
            config.expected_schedule_row_count == EXPECTED_SCHEDULE_ROW_COUNT,
            config.expected_schedule_row_count,
            "Step 34 expects 81 schedule rows",
        ),
        _check(
            "expected_motion_row_count",
            config.expected_motion_row_count == EXPECTED_MOTION_ROW_COUNT,
            config.expected_motion_row_count,
            "Step 34 expects 243 motion rows",
        ),
        _check(
            "expected_tracked_region_count",
            config.expected_tracked_region_count == EXPECTED_TRACKED_REGION_COUNT,
            config.expected_tracked_region_count,
            "Step 34 expects three tracked regions",
        ),
        _check("diagnostic_only_true", config.diagnostic_only is True, config.diagnostic_only, "interface must remain diagnostic-only"),
        _check("deterministic_true", config.deterministic is True, config.deterministic, "interface must be deterministic"),
        _check(
            "scope_note_valid",
            "diagnostic-only" in config.scope_note and "no-op" in config.scope_note,
            config.scope_note,
            "scope_note must state diagnostic-only and no-op behavior",
        ),
    ]
    for field in EXECUTION_FLAG_FIELDS:
        rows.append(_check(f"{field}_false", getattr(config, field) is False, getattr(config, field), f"{field} must be false"))
    rows.append(
        _check(
            "all_execution_flags_false",
            execution_flag_enabled_count(config) == 0,
            execution_flag_enabled_count(config),
            "all execution flags must remain disabled",
        )
    )
    return rows


def summarize_boundary_motion_config_validation(rows: list[dict]) -> dict:
    return {
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if bool(row["pass"])),
        "validation_pass": all(bool(row["pass"]) for row in rows),
    }


def execution_flags(config: BoundaryMotionInterfaceConfig) -> dict:
    return {field: bool(getattr(config, field)) for field in EXECUTION_FLAG_FIELDS}


def execution_flag_enabled_count(config: BoundaryMotionInterfaceConfig) -> int:
    return sum(1 for enabled in execution_flags(config).values() if enabled)


def _check(name: str, passed: bool, value, notes: str) -> dict:
    return {"check": name, "pass": bool(passed), "value": value, "notes": notes}


def _exists(root: Path, relative_path) -> bool:
    if relative_path is None:
        return False
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
