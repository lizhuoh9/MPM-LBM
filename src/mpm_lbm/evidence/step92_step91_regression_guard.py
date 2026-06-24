from __future__ import annotations

import json
from pathlib import Path


def build_step92_step91_regression_guard(
    root: Path,
    policy_path: str = "configs/step92_step91_regression_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    rows = [artifact_row(root, check) for check in policy["artifact_checks"]]
    plan_summary = read_json(
        root
        / "outputs/step91_first_user_simulation_10step_dry_run_plan/first_user_simulation_10step_dry_run_plan.json"
    )["summary"]
    guard_summary = read_json(
        root
        / "outputs/step91_first_user_simulation_10step_dry_run_guard/first_user_simulation_10step_dry_run_guard.json"
    )["summary"]
    output_summary = read_json(root / "outputs/step91_output_guard/output_guard.json")["summary"]
    artifact_summary = read_json(root / "outputs/step91_artifact_manifest/artifact_summary.json")
    summary = {
        "artifact_check_count": len(policy["artifact_checks"]),
        "artifact_pass_count": sum(1 for row in rows if row["pass"]),
        "pass_count": sum(1 for row in rows if row["pass"]),
        "planned_step92_activation_feature_count": plan_summary["planned_step92_activation_feature_count"],
        "row_count": len(rows),
        "step91_activation_feature_count": plan_summary["step91_activation_feature_count"],
        "step91_artifact_budget_pass": artifact_summary["artifact_budget_pass"],
        "step91_driver_run_dir_count": output_summary["step91_driver_run_dir_count"],
        "step91_first_user_simulation_10step_dry_run_guard_pass": guard_summary[
            "step91_first_user_simulation_10step_dry_run_guard_pass"
        ],
        "step91_first_user_simulation_10step_dry_run_plan_pass": plan_summary[
            "step91_first_user_simulation_10step_dry_run_plan_pass"
        ],
        "step91_output_guard_pass": output_summary["output_guard_pass"],
        "step91_particle_npy_count": output_summary["step91_particle_npy_count"],
        "step91_vtr_count": output_summary["step91_vtr_count"],
        "step92_allowed_n_lbm_steps": plan_summary["step92_allowed_n_lbm_steps"],
        "step92_allowed_row_name": plan_summary["step92_allowed_row_name"],
        "step92_step91_regression_guard_pass": False,
    }
    summary["step92_step91_regression_guard_pass"] = bool(
        rows
        and summary["artifact_pass_count"] == summary["artifact_check_count"]
        and summary["step91_artifact_budget_pass"] is True
        and summary["step91_activation_feature_count"] == int(policy["expected_step91_activation_feature_count"])
        and summary["planned_step92_activation_feature_count"]
        == int(policy["expected_planned_step92_activation_feature_count"])
        and summary["step92_allowed_row_name"] == policy["expected_step92_allowed_row_name"]
        and summary["step92_allowed_n_lbm_steps"] == int(policy["expected_step92_allowed_n_lbm_steps"])
        and summary["step91_driver_run_dir_count"] == int(policy["expected_step91_driver_run_dir_count"])
        and summary["step91_vtr_count"] == int(policy["expected_step91_vtr_count"])
        and summary["step91_particle_npy_count"] == int(policy["expected_step91_particle_npy_count"])
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
