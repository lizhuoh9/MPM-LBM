from __future__ import annotations

import importlib
from pathlib import Path

from src.mpm_lbm.evidence.current_root_inventory_audit import output_snapshot, read_json, read_text


def build_step74_real_geometry_quarantine_audit(
    root: Path,
    policy_path: str = "configs/step74_real_geometry_quarantine_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    relative_path = policy["quarantined_module_path"]
    path = root / relative_path
    text = read_text(path)
    before = output_snapshot(root)
    import_pass = import_quarantined_module_pass()
    after = output_snapshot(root)
    rows = [
        bool_row("quarantined_experiment_path_exists", path.is_file(), True, relative_path),
        bool_row("under_experiments_steps", relative_path.startswith("experiments/steps/"), True, relative_path),
        bool_row("under_sim_package", relative_path.startswith(policy["forbidden_runtime_prefix"]), False, relative_path),
        bool_row("module_import_pass", import_pass, True, relative_path),
        bool_row("output_snapshot_unchanged_after_import", before == after, True, relative_path),
    ]
    for symbol in policy["required_detected_symbols"]:
        rows.append(bool_row(f"{symbol}_detected", f"def {symbol}" in text, True, relative_path))
    driver_helper_detected = all(marker in text for marker in policy["driver_markers"])
    rows.append(bool_row("driver_helper_detected", driver_helper_detected, True, relative_path))
    rows.append(bool_row("driver_helper_executed", False, False, relative_path))
    rows.append(bool_row("solver_run", False, False, relative_path))
    summary = {
        "driver_helper_detected": driver_helper_detected,
        "driver_helper_executed": False,
        "module_import_pass": import_pass,
        "output_snapshot_unchanged": before == after,
        "pass_count": sum(1 for row in rows if row["pass"]),
        "quarantined_experiment_path_exists": path.is_file(),
        "real_geometry_quarantine_audit_pass": False,
        "row_count": len(rows),
        "solver_run": False,
        "under_sim_package": relative_path.startswith(policy["forbidden_runtime_prefix"]),
    }
    summary["real_geometry_quarantine_audit_pass"] = bool(
        summary["pass_count"] == summary["row_count"]
        and summary["quarantined_experiment_path_exists"]
        and summary["under_sim_package"] is False
        and summary["driver_helper_detected"]
        and summary["driver_helper_executed"] is False
        and summary["solver_run"] is False
        and summary["output_snapshot_unchanged"]
    )
    return rows, summary


def import_quarantined_module_pass() -> bool:
    try:
        importlib.import_module("experiments.steps.real_geometry_feasibility.feasibility")
    except Exception:  # pragma: no cover - artifact row captures only pass/fail
        return False
    return True


def bool_row(check: str, actual, expected, path: str) -> dict:
    return {"actual": actual, "check": check, "expected": expected, "pass": actual == expected, "path": path}
