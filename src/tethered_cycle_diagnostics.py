import os
from pathlib import Path


FREE_BODY_MARKERS = (
    "free_body",
    "freebody",
    "rigid_body_state",
    "body_position_state",
    "swimming_displacement",
)

BODY_TRAJECTORY_MARKERS = (
    "body_trajectory",
    "trajectory",
    "swimming_path",
)


def summarize_no_free_body_state(configs: list[dict], output_root) -> dict:
    output_path = _resolve_path(output_root)
    free_body_files = _find_marker_files(output_path)
    body_trajectory_files = _find_body_trajectory_files(output_path)
    target_u_zero = all(tuple(float(value) for value in config.get("target_u_lbm", [])) == (0.0, 0.0, 0.0) for config in configs)
    summary = {
        "guard": "Step 38 tethered no-free-body guard",
        "config_count": len(configs),
        "free_body_state_file_count": len(free_body_files),
        "free_body_state_files": [str(path).replace("\\", "/") for path in free_body_files],
        "body_trajectory_output_count": len(body_trajectory_files),
        "body_trajectory_output_files": [str(path).replace("\\", "/") for path in body_trajectory_files],
        "rigid_body_integrator_enabled": any(_truthy(config.get("rigid_body_integrator_enabled", False)) for config in configs),
        "body_position_state_enabled": any(_truthy(config.get("body_position_state_enabled", False)) for config in configs),
        "swimming_displacement_claim_enabled": any(_truthy(config.get("swimming_displacement_claim_enabled", False)) for config in configs),
        "target_u_lbm_zero_for_cycle_configs": bool(target_u_zero),
        "centroid_drift_is_diagnostic_only": True,
        "notes": "tethered diagnostics only; no free-body integration and no swimming displacement claim",
    }
    summary["guard_pass"] = bool(
        summary["config_count"] == 4
        and summary["free_body_state_file_count"] == 0
        and summary["body_trajectory_output_count"] == 0
        and not summary["rigid_body_integrator_enabled"]
        and not summary["body_position_state_enabled"]
        and not summary["swimming_displacement_claim_enabled"]
        and summary["target_u_lbm_zero_for_cycle_configs"]
    )
    return summary


def summarize_multicycle_tethered_guard(configs: list[dict], output_root) -> dict:
    summary = summarize_no_free_body_state(configs, output_root)
    summary["guard"] = "Step 39 multicycle tethered no-free-body guard"
    summary["notes"] = "multicycle tethered diagnostics only; no body trajectory, free-body integration, or swimming displacement claim"
    return summary


def guard_rows(summary: dict) -> list[dict]:
    return [
        _row("free_body_state_file_count", int(summary["free_body_state_file_count"]) == 0, summary["free_body_state_file_count"], "no free-body state files are written"),
        _row("body_trajectory_output_count", int(summary.get("body_trajectory_output_count", 0)) == 0, summary.get("body_trajectory_output_count", 0), "no body trajectory outputs are written"),
        _row("rigid_body_integrator_enabled", summary["rigid_body_integrator_enabled"] is False, summary["rigid_body_integrator_enabled"], "no rigid-body swimming integrator is enabled"),
        _row("body_position_state_enabled", summary["body_position_state_enabled"] is False, summary["body_position_state_enabled"], "no body position state is enabled"),
        _row("swimming_displacement_claim_enabled", summary["swimming_displacement_claim_enabled"] is False, summary["swimming_displacement_claim_enabled"], "no swimming displacement claim is enabled"),
        _row("target_u_lbm_zero_for_cycle_configs", summary["target_u_lbm_zero_for_cycle_configs"] is True, summary["target_u_lbm_zero_for_cycle_configs"], "all cycle configs use zero background target velocity"),
    ]


def _row(check, passed, value, notes) -> dict:
    return {"check": check, "pass": bool(passed), "value": value, "notes": notes}


def _find_marker_files(output_path: Path) -> list[Path]:
    if not output_path.exists():
        return []
    matches = []
    for path in output_path.rglob("*"):
        if not path.is_file():
            continue
        lowered = path.name.lower()
        if any(marker in lowered for marker in FREE_BODY_MARKERS):
            matches.append(path)
    return sorted(matches)


def _find_body_trajectory_files(output_path: Path) -> list[Path]:
    if not output_path.exists():
        return []
    matches = []
    for path in output_path.rglob("*"):
        if not path.is_file():
            continue
        lowered = path.name.lower()
        if any(marker in lowered for marker in BODY_TRAJECTORY_MARKERS):
            matches.append(path)
    return sorted(matches)


def _truthy(value) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "enabled"}


def _resolve_path(path) -> Path:
    path_obj = Path(os.fspath(path))
    if path_obj.is_absolute():
        return path_obj
    return Path(__file__).resolve().parents[1] / path_obj
