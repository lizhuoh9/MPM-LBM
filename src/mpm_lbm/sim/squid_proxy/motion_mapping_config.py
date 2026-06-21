from dataclasses import asdict, dataclass
import json
import os
from pathlib import Path


REQUIRED_TRACKED_REGIONS = (
    "mantle_outer",
    "mantle_cavity_proxy",
    "funnel_outlet_proxy",
)

EXPECTED_GRID_SIZES = (32, 48, 64)


@dataclass(frozen=True)
class SquidMotionMappingConfig:
    mapping_id: str
    schedule_config_path: str
    region_config_path: str
    geometry_config_path: str
    sample_count: int
    grid_sizes: tuple[int, ...]
    tracked_regions: tuple[str, ...]
    mantle_motion_model: str
    cavity_motion_model: str
    funnel_motion_model: str
    driver_integration_enabled: bool = False
    lbm_wall_velocity_enabled: bool = False
    jet_model_enabled: bool = False
    actuation_enabled: bool = False
    deterministic: bool = True
    scope_note: str = "motion diagnostics only; no driver integration"

    def __post_init__(self):
        object.__setattr__(self, "sample_count", int(self.sample_count))
        object.__setattr__(self, "grid_sizes", tuple(int(value) for value in self.grid_sizes))
        object.__setattr__(self, "tracked_regions", tuple(str(value) for value in self.tracked_regions))
        object.__setattr__(self, "driver_integration_enabled", bool(self.driver_integration_enabled))
        object.__setattr__(self, "lbm_wall_velocity_enabled", bool(self.lbm_wall_velocity_enabled))
        object.__setattr__(self, "jet_model_enabled", bool(self.jet_model_enabled))
        object.__setattr__(self, "actuation_enabled", bool(self.actuation_enabled))
        object.__setattr__(self, "deterministic", bool(self.deterministic))

    @classmethod
    def from_json(cls, path):
        with Path(path).open("r", encoding="utf-8") as f:
            return cls(**json.load(f))

    def to_dict(self):
        payload = asdict(self)
        payload["grid_sizes"] = list(self.grid_sizes)
        payload["tracked_regions"] = list(self.tracked_regions)
        return payload


def validate_motion_mapping_config(config: SquidMotionMappingConfig, root=None) -> list[dict]:
    root_path = Path.cwd() if root is None else Path(root)
    rows = [
        _check("mapping_id_present", bool(config.mapping_id), config.mapping_id, "mapping_id must be nonempty"),
        _check("schedule_config_path_exists", _exists(root_path, config.schedule_config_path), config.schedule_config_path, "Step 32 schedule config must exist"),
        _check("region_config_path_exists", _exists(root_path, config.region_config_path), config.region_config_path, "Step 30 region config must exist"),
        _check("geometry_config_path_exists", _exists(root_path, config.geometry_config_path), config.geometry_config_path, "Step 30 geometry config must exist"),
        _check("sample_count_positive", config.sample_count > 0, config.sample_count, "sample_count must be positive"),
        _check("grid_sizes_positive", all(value > 0 for value in config.grid_sizes), list(config.grid_sizes), "grid sizes must be positive"),
        _check("grid_sizes_expected", config.grid_sizes == EXPECTED_GRID_SIZES, list(config.grid_sizes), "grid sizes must be [32, 48, 64]"),
        _check("tracked_regions_include_mantle_outer", "mantle_outer" in config.tracked_regions, list(config.tracked_regions), "mantle_outer must be tracked"),
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
        _check("tracked_regions_expected", config.tracked_regions == REQUIRED_TRACKED_REGIONS, list(config.tracked_regions), "tracked regions must match Step 33 contract"),
        _check("mantle_motion_model_valid", config.mantle_motion_model == "radial_scale_proxy", config.mantle_motion_model, "mantle model must be radial_scale_proxy"),
        _check("cavity_motion_model_valid", config.cavity_motion_model == "volume_scale_proxy", config.cavity_motion_model, "cavity model must be volume_scale_proxy"),
        _check("funnel_motion_model_valid", config.funnel_motion_model == "aperture_scale_proxy", config.funnel_motion_model, "funnel model must be aperture_scale_proxy"),
        _check("deterministic_enabled", config.deterministic is True, config.deterministic, "mapping must be deterministic"),
        _check("driver_integration_disabled", config.driver_integration_enabled is False, config.driver_integration_enabled, "Step 33 must not integrate with driver"),
        _check("lbm_wall_velocity_disabled", config.lbm_wall_velocity_enabled is False, config.lbm_wall_velocity_enabled, "Step 33 must not enable LBM wall velocity"),
        _check("jet_model_disabled", config.jet_model_enabled is False, config.jet_model_enabled, "Step 33 must not enable a jet model"),
        _check("actuation_disabled", config.actuation_enabled is False, config.actuation_enabled, "Step 33 must not enable actuation"),
        _check(
            "scope_note_valid",
            "motion diagnostics only" in config.scope_note and "no driver integration" in config.scope_note,
            config.scope_note,
            "scope_note must state diagnostics-only and no driver integration",
        ),
    ]
    return rows


def summarize_motion_mapping_config_validation(rows: list[dict]) -> dict:
    return {
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if bool(row["pass"])),
        "validation_pass": all(bool(row["pass"]) for row in rows),
    }


def _check(name: str, passed: bool, value, notes: str) -> dict:
    return {"check": name, "pass": bool(passed), "value": value, "notes": notes}


def _exists(root: Path, relative_path: str) -> bool:
    path = Path(os.fspath(relative_path))
    if not path.is_absolute():
        path = root / path
    return path.is_file()
