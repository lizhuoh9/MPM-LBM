from dataclasses import asdict, dataclass
import json
import math
import os
from pathlib import Path


REQUIRED_TRACKED_REGIONS = (
    "mantle_outer",
    "mantle_cavity_proxy",
    "funnel_outlet_proxy",
)

EXPECTED_GRID_SIZES = (32, 48, 64)


@dataclass(frozen=True)
class GeometryDisplacementConfig:
    displacement_id: str
    schedule_config_path: str
    motion_mapping_config_path: str
    region_config_path: str
    geometry_config_path: str
    tracked_regions: tuple[str, ...]
    context_regions: tuple[str, ...]
    sample_count: int
    phase_sample_count: int
    grid_sizes: tuple[int, ...]
    mantle_displacement_model: str
    cavity_displacement_model: str
    funnel_displacement_model: str
    max_displacement_norm_allowed: float
    write_dense_displacement_field: bool = False
    write_displaced_particles: bool = False
    apply_to_driver: bool = False
    apply_to_lbm: bool = False
    apply_to_mpm: bool = False
    apply_to_projection: bool = False
    update_dynamic_solid: bool = False
    driver_integration_enabled: bool = False
    deterministic: bool = True
    scope_note: str = "geometry displacement diagnostics only; no driver-coupled geometry update"

    def __post_init__(self):
        object.__setattr__(self, "tracked_regions", tuple(str(value) for value in self.tracked_regions))
        object.__setattr__(self, "context_regions", tuple(str(value) for value in self.context_regions))
        object.__setattr__(self, "sample_count", int(self.sample_count))
        object.__setattr__(self, "phase_sample_count", int(self.phase_sample_count))
        object.__setattr__(self, "grid_sizes", tuple(int(value) for value in self.grid_sizes))
        object.__setattr__(self, "max_displacement_norm_allowed", float(self.max_displacement_norm_allowed))
        for field in (
            "write_dense_displacement_field",
            "write_displaced_particles",
            "apply_to_driver",
            "apply_to_lbm",
            "apply_to_mpm",
            "apply_to_projection",
            "update_dynamic_solid",
            "driver_integration_enabled",
            "deterministic",
        ):
            object.__setattr__(self, field, bool(getattr(self, field)))

    @classmethod
    def from_json(cls, path):
        with Path(path).open("r", encoding="utf-8") as f:
            return cls(**json.load(f))

    def to_dict(self):
        payload = asdict(self)
        payload["tracked_regions"] = list(self.tracked_regions)
        payload["context_regions"] = list(self.context_regions)
        payload["grid_sizes"] = list(self.grid_sizes)
        return payload


def validate_geometry_displacement_config(config: GeometryDisplacementConfig, root=None) -> list[dict]:
    root_path = Path.cwd() if root is None else Path(root)
    rows = [
        _check("displacement_id_expected", config.displacement_id == "step42_squid_proxy_geometry_displacement_diagnostics", config.displacement_id, "Step 42 displacement id must be stable"),
        _check("schedule_config_path_exists", _exists(root_path, config.schedule_config_path), config.schedule_config_path, "Step 32 schedule config must exist"),
        _check("motion_mapping_config_path_exists", _exists(root_path, config.motion_mapping_config_path), config.motion_mapping_config_path, "Step 33 motion mapping config must exist"),
        _check("region_config_path_exists", _exists(root_path, config.region_config_path), config.region_config_path, "Step 30 region config must exist"),
        _check("geometry_config_path_exists", _exists(root_path, config.geometry_config_path), config.geometry_config_path, "Step 30 geometry config must exist"),
        _check("sample_count_expected", config.sample_count == 32768, config.sample_count, "sample_count must remain 32768"),
        _check("phase_sample_count_expected", config.phase_sample_count == 81, config.phase_sample_count, "phase_sample_count must remain 81"),
        _check("grid_sizes_expected", config.grid_sizes == EXPECTED_GRID_SIZES, list(config.grid_sizes), "grid sizes must be [32, 48, 64]"),
        _check("tracked_regions_expected", config.tracked_regions == REQUIRED_TRACKED_REGIONS, list(config.tracked_regions), "tracked regions must match the Step 42 contract"),
        _check("mantle_model_valid", config.mantle_displacement_model == "radial_scale_proxy", config.mantle_displacement_model, "mantle model must be radial_scale_proxy"),
        _check("cavity_model_valid", config.cavity_displacement_model == "volume_scale_proxy", config.cavity_displacement_model, "cavity model must be volume_scale_proxy"),
        _check("funnel_model_valid", config.funnel_displacement_model == "aperture_scale_proxy", config.funnel_displacement_model, "funnel model must be aperture_scale_proxy"),
        _check("max_displacement_norm_finite", math.isfinite(config.max_displacement_norm_allowed), config.max_displacement_norm_allowed, "max displacement bound must be finite"),
        _check("max_displacement_norm_expected", config.max_displacement_norm_allowed == 0.25, config.max_displacement_norm_allowed, "max displacement bound must be 0.25"),
        _check("dense_field_disabled", config.write_dense_displacement_field is False, config.write_dense_displacement_field, "Step 42 must not write dense displacement fields"),
        _check("displaced_particles_disabled", config.write_displaced_particles is False, config.write_displaced_particles, "Step 42 must not write displaced particles"),
        _check("apply_to_driver_disabled", config.apply_to_driver is False, config.apply_to_driver, "Step 42 must not apply to FSIDriver3D"),
        _check("apply_to_lbm_disabled", config.apply_to_lbm is False, config.apply_to_lbm, "Step 42 must not apply to LBM"),
        _check("apply_to_mpm_disabled", config.apply_to_mpm is False, config.apply_to_mpm, "Step 42 must not apply to MPM"),
        _check("apply_to_projection_disabled", config.apply_to_projection is False, config.apply_to_projection, "Step 42 must not apply to projection"),
        _check("update_dynamic_solid_disabled", config.update_dynamic_solid is False, config.update_dynamic_solid, "Step 42 must not update dynamic_solid"),
        _check("driver_integration_disabled", config.driver_integration_enabled is False, config.driver_integration_enabled, "driver integration must remain disabled"),
        _check("deterministic_enabled", config.deterministic is True, config.deterministic, "Step 42 must be deterministic"),
        _check("scope_note_valid", "geometry displacement diagnostics only" in config.scope_note and "no driver-coupled" in config.scope_note, config.scope_note, "scope note must state diagnostic-only scope"),
    ]
    return rows


def summarize_geometry_displacement_config_validation(rows: list[dict], config: GeometryDisplacementConfig) -> dict:
    return {
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if bool(row["pass"])),
        "validation_pass": all(bool(row["pass"]) for row in rows),
        "tracked_region_count": len(config.tracked_regions),
        "phase_sample_count": int(config.phase_sample_count),
        "grid_sizes": list(config.grid_sizes),
    }


def _check(name: str, passed: bool, value, notes: str) -> dict:
    return {"check": name, "pass": bool(passed), "value": value, "notes": notes}


def _exists(root: Path, relative_path: str) -> bool:
    path = Path(os.fspath(relative_path))
    if not path.is_absolute():
        path = root / path
    return path.is_file()
