from __future__ import annotations

import json
from pathlib import Path


def build_step88_step87_regression_guard(
    root: Path,
    policy_path: str = "configs/step88_step87_regression_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    rows = [artifact_row(root, check) for check in policy["artifact_checks"]]
    plan_summary = read_json(
        root
        / "outputs/step87_runtime_geometry_wall_velocity_squid_proxy_combined_activation_plan/runtime_geometry_wall_velocity_squid_proxy_combined_activation_plan.json"
    )["summary"]
    output_summary = read_json(root / "outputs/step87_output_guard/output_guard.json")["summary"]
    summary = {
        "artifact_check_count": len(policy["artifact_checks"]),
        "artifact_pass_count": sum(1 for row in rows if row["pass"]),
        "pass_count": sum(1 for row in rows if row["pass"]),
        "planned_step88_activation_feature_count": plan_summary["planned_step88_activation_feature_count"],
        "row_count": len(rows),
        "step87_activation_feature_count": plan_summary["step87_activation_feature_count"],
        "step87_driver_run_dir_count": output_summary["step87_driver_run_dir_count"],
        "step87_particle_npy_count": output_summary["step87_particle_npy_count"],
        "step88_step87_regression_guard_pass": False,
        "step87_vtr_count": output_summary["step87_vtr_count"],
    }
    summary["step88_step87_regression_guard_pass"] = bool(
        rows
        and summary["artifact_pass_count"] == summary["artifact_check_count"]
        and summary["step87_activation_feature_count"] == int(policy["expected_step87_activation_feature_count"])
        and summary["planned_step88_activation_feature_count"]
        == int(policy["expected_planned_step88_activation_feature_count"])
        and summary["step87_driver_run_dir_count"] == 0
        and summary["step87_vtr_count"] == 0
        and summary["step87_particle_npy_count"] == 0
    )
    return rows, summary


def artifact_row(root: Path, check: dict) -> dict:
    actual = artifact_value(root, check["artifact_path"], check["summary_key"])
    return {
        "actual": actual,
        "artifact_path": check["artifact_path"],
        "check": check["check"],
        "expected": check["expected"],
        "pass": actual == check["expected"],
        "summary_key": check["summary_key"],
    }


def artifact_value(root: Path, artifact_path: str, summary_key: str):
    payload = read_json(Path(root) / artifact_path)
    return payload.get("summary", payload).get(summary_key)


def read_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)
