import json
import os
from pathlib import Path

from src.mpm_lbm.sim.motion.geometry_motion_config import (
    GeometryMotionInterfaceConfig,
    mutation_flags,
    summarize_geometry_motion_config_validation,
    validate_geometry_motion_interface_config,
)


GEOMETRY_MOTION_SCOPE_NOTE = "Step 43 diagnostic-only geometry motion driver interface; no geometry mutation"


def load_geometry_motion_interface_config(path) -> GeometryMotionInterfaceConfig:
    return GeometryMotionInterfaceConfig.from_json(_resolve_path(path))


def assert_geometry_motion_noop_flags(config: GeometryMotionInterfaceConfig) -> None:
    enabled = [field for field, value in mutation_flags(config).items() if value]
    if enabled:
        raise ValueError(f"geometry motion interface has mutation flags enabled: {enabled}")
    if config.application_mode != "diagnostic_only" or config.diagnostic_only is not True:
        raise ValueError("geometry motion interface must remain diagnostic_only")


def summarize_geometry_motion_interface(config: GeometryMotionInterfaceConfig, root=None) -> dict:
    root_path = _repo_root() if root is None else Path(root)
    rows = validate_geometry_motion_interface_config(config, root=root_path)
    validation = summarize_geometry_motion_config_validation(rows, config, root=root_path)
    quality = _read_optional_summary(root_path / "outputs/step42_displacement_quality/displacement_quality.json")
    repeatability = _read_optional_summary(root_path / "outputs/step42_displacement_repeatability/displacement_repeatability.json")
    closure = _read_optional_summary(root_path / "outputs/step42_cycle_closure_diagnostics/cycle_closure_diagnostics.json")
    summary = {
        "geometry_motion_id": config.geometry_motion_id,
        "geometry_motion_mode": config.geometry_motion_mode,
        "application_mode": config.application_mode,
        "diagnostic_only": bool(config.diagnostic_only),
        "config_validation_pass": bool(validation["validation_pass"]),
        "config_validation_row_count": int(validation["row_count"]),
        "config_validation_pass_count": int(validation["pass_count"]),
        "displacement_config_path": config.displacement_config_path,
        "displacement_artifact_path": config.displacement_artifact_path,
        "displacement_row_count": int(validation["displacement_row_count"]),
        "phase_sample_count": int(validation["phase_sample_count"]),
        "tracked_region_count": int(validation["tracked_region_count"]),
        "tracked_regions": validation["tracked_regions"],
        "max_displacement_norm": float(validation["max_displacement_norm"]),
        "displacement_finite_pass": bool(validation["displacement_finite_pass"]),
        "displacement_bounds_pass": bool(validation["displacement_bounds_pass"]),
        "quality_pass": bool(quality.get("quality_pass", False)),
        "cycle_closure_pass": bool(closure.get("cycle_closure_pass", False)),
        "repeatability_pass": bool(repeatability.get("repeatability_pass", False)),
        "scope_note": GEOMETRY_MOTION_SCOPE_NOTE,
    }
    summary.update(mutation_flags(config))
    summary["mutation_flag_enabled_count"] = sum(1 for value in mutation_flags(config).values() if value)
    summary["no_op_pass"] = bool(
        summary["config_validation_pass"]
        and summary["diagnostic_only"]
        and summary["mutation_flag_enabled_count"] == 0
        and summary["displacement_row_count"] == 243
        and summary["phase_sample_count"] == 81
        and summary["tracked_region_count"] == 3
        and summary["displacement_finite_pass"]
        and summary["displacement_bounds_pass"]
        and summary["quality_pass"]
        and summary["cycle_closure_pass"]
        and summary["repeatability_pass"]
    )
    return summary


def build_geometry_motion_interface_report(config_path, geometry_motion_mode="prescribed_kinematic") -> dict:
    config = load_geometry_motion_interface_config(config_path)
    if config.geometry_motion_mode != geometry_motion_mode:
        raise ValueError(f"geometry_motion_mode mismatch: {config.geometry_motion_mode} != {geometry_motion_mode}")
    assert_geometry_motion_noop_flags(config)
    validation_rows = validate_geometry_motion_interface_config(config, root=_repo_root())
    validation_summary = summarize_geometry_motion_config_validation(validation_rows, config, root=_repo_root())
    if not validation_summary["validation_pass"]:
        raise ValueError(f"geometry motion interface config validation failed: {validation_rows}")
    summary = summarize_geometry_motion_interface(config, root=_repo_root())
    return {
        "summary": summary,
        "config": config.to_dict(),
        "validation_summary": validation_summary,
        "validation_rows": validation_rows,
    }


def write_geometry_motion_interface_report(config_path, report_path=None, geometry_motion_mode="prescribed_kinematic") -> dict:
    payload = build_geometry_motion_interface_report(config_path, geometry_motion_mode=geometry_motion_mode)
    if report_path is not None:
        _write_json(report_path, payload)
    return payload


def _read_optional_summary(path: Path) -> dict:
    if not path.is_file():
        return {}
    with path.open("r", encoding="utf-8") as f:
        payload = json.load(f)
    return payload.get("summary", payload)


def _write_json(path, payload) -> None:
    resolved = _resolve_path(path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    with resolved.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=True)
        f.write("\n")


def _resolve_path(path) -> Path:
    path_obj = Path(os.fspath(path))
    if path_obj.is_absolute():
        return path_obj
    return _repo_root() / path_obj


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]
