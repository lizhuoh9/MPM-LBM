from __future__ import annotations

import json
from pathlib import Path


def build_step94_step90_regression_guard(
    root: Path,
    policy_path: str = "configs/step94_step90_regression_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    rows = [artifact_row(root, check) for check in policy["artifact_checks"]]
    matrix_summary = read_json(
        root / "outputs/step90_first_user_simulation_dry_run_matrix/first_user_simulation_dry_run_matrix.json"
    )["summary"]
    quality_summary = read_json(
        root / "outputs/step90_first_user_simulation_dry_run_quality/first_user_simulation_dry_run_quality.json"
    )["summary"]
    activation_summary = read_json(root / "outputs/step90_activation_guard/activation_guard.json")["summary"]
    output_summary = read_json(root / "outputs/step90_output_guard/output_guard.json")["summary"]
    artifact_summary = read_json(root / "outputs/step90_artifact_manifest/artifact_summary.json")
    summary = {
        "artifact_check_count": len(policy["artifact_checks"]),
        "artifact_pass_count": sum(1 for row in rows if row["pass"]),
        "pass_count": sum(1 for row in rows if row["pass"]),
        "row_count": len(rows),
        "step90_activation_feature_count": activation_summary["activation_feature_count"],
        "step90_activation_guard_pass": activation_summary["step90_activation_guard_pass"],
        "step90_artifact_budget_pass": artifact_summary["artifact_budget_pass"],
        "step90_combined_runtime_geometry_wall_velocity_enabled_count": activation_summary[
            "combined_runtime_geometry_wall_velocity_enabled_count"
        ],
        "step90_completed_lbm_steps": matrix_summary["min_completed_lbm_steps"],
        "step90_first_user_simulation_dry_run_matrix_pass": matrix_summary[
            "step90_first_user_simulation_dry_run_matrix_pass"
        ],
        "step90_first_user_simulation_dry_run_quality_pass": quality_summary[
            "step90_first_user_simulation_dry_run_quality_pass"
        ],
        "step90_link_area_enabled_count": activation_summary["link_area_enabled_count"],
        "step90_output_guard_pass": output_summary["output_guard_pass"],
        "step90_particle_npy_count": output_summary["step90_particle_npy_count"],
        "step90_real_geometry_candidate_enabled_count": activation_summary["real_geometry_candidate_enabled_count"],
        "step90_runtime_geometry_enabled_count": activation_summary["runtime_geometry_enabled_count"],
        "step90_squid_proxy_enabled_count": activation_summary["squid_proxy_enabled_count"],
        "step90_vtr_count": output_summary["step90_vtr_count"],
        "step90_wall_velocity_enabled_count": activation_summary["wall_velocity_enabled_count"],
        "step94_step90_regression_guard_pass": False,
    }
    summary["step94_step90_regression_guard_pass"] = bool(
        rows
        and summary["artifact_pass_count"] == summary["artifact_check_count"]
        and summary["step90_first_user_simulation_dry_run_matrix_pass"] is True
        and summary["step90_first_user_simulation_dry_run_quality_pass"] is True
        and summary["step90_activation_guard_pass"] is True
        and summary["step90_output_guard_pass"] is True
        and summary["step90_artifact_budget_pass"] is True
        and summary["step90_activation_feature_count"] == int(policy["expected_step90_activation_feature_count"])
        and summary["step90_completed_lbm_steps"] == int(policy["expected_step90_completed_lbm_steps"])
        and summary["step90_squid_proxy_enabled_count"] == 1
        and summary["step90_runtime_geometry_enabled_count"] == 1
        and summary["step90_wall_velocity_enabled_count"] == 1
        and summary["step90_combined_runtime_geometry_wall_velocity_enabled_count"] == 1
        and summary["step90_real_geometry_candidate_enabled_count"]
        == int(policy["expected_step90_real_geometry_candidate_enabled_count"])
        and summary["step90_link_area_enabled_count"] == int(policy["expected_step90_link_area_enabled_count"])
        and summary["step90_vtr_count"] == int(policy["expected_step90_vtr_count"])
        and summary["step90_particle_npy_count"] == int(policy["expected_step90_particle_npy_count"])
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
