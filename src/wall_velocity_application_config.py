from dataclasses import asdict, dataclass
import json
import math
import os
from pathlib import Path


VALID_WALL_VELOCITY_APPLICATION_MODES = ("solid_vel_experimental",)
VALID_WALL_VELOCITY_APPLICATION_POLICIES = ("additive_capped", "replace_capped")

APPLICATION_FLAG_FIELDS = (
    "apply_to_lbm_solid_vel",
    "apply_to_lbm_populations",
    "apply_to_mpm",
    "apply_to_projector",
    "modify_bounceback_formula",
    "jet_model_enabled",
    "actuation_claim_enabled",
    "diagnostic_report_enabled",
)


@dataclass(frozen=True)
class WallVelocityApplicationConfig:
    application_id: str
    wall_velocity_config_path: str
    boundary_motion_config_path: str
    geometry_config_path: str
    region_config_path: str
    application_mode: str = "solid_vel_experimental"
    target_lbm_field: str = "solid_vel"
    application_policy: str = "additive_capped"
    wall_velocity_scale: float = 0.05
    wall_velocity_cap_lbm: float = 0.01
    apply_to_lbm_solid_vel: bool = True
    apply_to_lbm_populations: bool = False
    apply_to_mpm: bool = False
    apply_to_projector: bool = False
    modify_bounceback_formula: bool = False
    jet_model_enabled: bool = False
    actuation_claim_enabled: bool = False
    diagnostic_report_enabled: bool = True
    scope_note: str = "Step 36 opt-in experimental solid_vel application smoke only"

    def __post_init__(self):
        object.__setattr__(self, "wall_velocity_scale", float(self.wall_velocity_scale))
        object.__setattr__(self, "wall_velocity_cap_lbm", float(self.wall_velocity_cap_lbm))
        for field in APPLICATION_FLAG_FIELDS:
            object.__setattr__(self, field, bool(getattr(self, field)))

    @classmethod
    def from_json(cls, path):
        with _resolve_path(path).open("r", encoding="utf-8") as f:
            return cls(**json.load(f))

    def to_dict(self):
        return asdict(self)


def validate_wall_velocity_application_config(config: WallVelocityApplicationConfig, root=None) -> list[dict]:
    root_path = _repo_root() if root is None else Path(root)
    rows = [
        _check("application_id_present", bool(config.application_id), config.application_id, "application_id must be nonempty"),
        _check("wall_velocity_config_path_exists", _exists(root_path, config.wall_velocity_config_path), config.wall_velocity_config_path, "Step 35 wall velocity config must exist"),
        _check("boundary_motion_config_path_exists", _exists(root_path, config.boundary_motion_config_path), config.boundary_motion_config_path, "Step 34 boundary-motion config must exist"),
        _check("geometry_config_path_exists", _exists(root_path, config.geometry_config_path), config.geometry_config_path, "Step 30 geometry config must exist"),
        _check("region_config_path_exists", _exists(root_path, config.region_config_path), config.region_config_path, "Step 30 region config must exist"),
        _check("application_mode_valid", config.application_mode == "solid_vel_experimental", config.application_mode, "application_mode must be solid_vel_experimental"),
        _check("target_lbm_field_valid", config.target_lbm_field == "solid_vel", config.target_lbm_field, "target_lbm_field must be solid_vel"),
        _check("application_policy_valid", config.application_policy in VALID_WALL_VELOCITY_APPLICATION_POLICIES, config.application_policy, "application_policy must be supported"),
        _check("wall_velocity_scale_valid", math.isfinite(config.wall_velocity_scale) and 0.0 < config.wall_velocity_scale <= 1.0, config.wall_velocity_scale, "wall_velocity_scale must be in (0, 1]"),
        _check("wall_velocity_cap_lbm_valid", math.isfinite(config.wall_velocity_cap_lbm) and 0.0 < config.wall_velocity_cap_lbm <= 0.05, config.wall_velocity_cap_lbm, "wall_velocity_cap_lbm must be in (0, 0.05]"),
        _check("apply_to_lbm_solid_vel_true", config.apply_to_lbm_solid_vel is True, config.apply_to_lbm_solid_vel, "Step 36 applies only to lbm.solid_vel"),
        _check("apply_to_lbm_populations_false", config.apply_to_lbm_populations is False, config.apply_to_lbm_populations, "Step 36 must not write LBM populations"),
        _check("apply_to_mpm_false", config.apply_to_mpm is False, config.apply_to_mpm, "Step 36 must not write MPM state"),
        _check("apply_to_projector_false", config.apply_to_projector is False, config.apply_to_projector, "Step 36 must not write projector state"),
        _check("modify_bounceback_formula_false", config.modify_bounceback_formula is False, config.modify_bounceback_formula, "Step 36 must not modify bounce-back formulas"),
        _check("jet_model_enabled_false", config.jet_model_enabled is False, config.jet_model_enabled, "Step 36 must not enable a jet model"),
        _check("actuation_claim_enabled_false", config.actuation_claim_enabled is False, config.actuation_claim_enabled, "Step 36 must not enable actuation claims"),
        _check("diagnostic_report_enabled_true", config.diagnostic_report_enabled is True, config.diagnostic_report_enabled, "Step 36 must write diagnostic reports"),
        _check(
            "scope_note_valid",
            "opt-in experimental" in config.scope_note and "solid_vel" in config.scope_note,
            config.scope_note,
            "scope_note must state opt-in experimental solid_vel application",
        ),
    ]
    return rows


def summarize_wall_velocity_application_config_validation(rows: list[dict], config: WallVelocityApplicationConfig | None = None) -> dict:
    summary = {
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if bool(row["pass"])),
        "validation_pass": all(bool(row["pass"]) for row in rows),
    }
    if config is not None:
        summary.update(
            {
                "application_id": config.application_id,
                "application_mode": config.application_mode,
                "target_lbm_field": config.target_lbm_field,
                "application_policy": config.application_policy,
                "wall_velocity_scale": config.wall_velocity_scale,
                "wall_velocity_cap_lbm": config.wall_velocity_cap_lbm,
                "apply_to_lbm_solid_vel": config.apply_to_lbm_solid_vel,
                "apply_to_lbm_populations": config.apply_to_lbm_populations,
                "apply_to_mpm": config.apply_to_mpm,
                "apply_to_projector": config.apply_to_projector,
                "modify_bounceback_formula": config.modify_bounceback_formula,
                "jet_model_enabled": config.jet_model_enabled,
                "actuation_claim_enabled": config.actuation_claim_enabled,
                "diagnostic_report_enabled": config.diagnostic_report_enabled,
            }
        )
    return summary


def assert_valid_wall_velocity_application_config(config: WallVelocityApplicationConfig, root=None) -> None:
    rows = validate_wall_velocity_application_config(config, root=root)
    summary = summarize_wall_velocity_application_config_validation(rows, config=config)
    if not bool(summary["validation_pass"]):
        failed = [row for row in rows if not row["pass"]]
        raise ValueError(f"Step 36 wall velocity application config validation failed: {failed}")


def _check(name: str, passed: bool, value, notes: str) -> dict:
    return {"check": name, "pass": bool(passed), "value": value, "notes": notes}


def _exists(root: Path, relative_path: str) -> bool:
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
