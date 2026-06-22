from __future__ import annotations

import json
from pathlib import Path


def build_step82_step81_regression_guard(
    root: Path,
    policy_path: str = "configs/step82_step81_regression_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    rows = [artifact_row(root, check) for check in policy["artifact_checks"]]
    summary = {
        "artifact_check_count": len(policy["artifact_checks"]),
        "artifact_pass_count": sum(1 for row in rows if row["pass"]),
        "pass_count": sum(1 for row in rows if row["pass"]),
        "planned_step82_activation_feature_count": artifact_value(
            root,
            "outputs/step81_wall_velocity_single_feature_activation_plan/wall_velocity_single_feature_activation_plan.json",
            "planned_step82_activation_feature_count",
        ),
        "row_count": len(rows),
        "step81_activation_feature_count": artifact_value(
            root,
            "outputs/step81_wall_velocity_single_feature_activation_plan/wall_velocity_single_feature_activation_plan.json",
            "step81_activation_feature_count",
        ),
        "step81_driver_run_dir_count": artifact_value(
            root,
            "outputs/step81_artifact_manifest/artifact_summary.json",
            "step81_driver_run_dir_count",
        ),
        "step81_particle_npy_count": artifact_value(
            root,
            "outputs/step81_artifact_manifest/artifact_summary.json",
            "step81_particle_npy_count",
        ),
        "step81_vtr_count": artifact_value(root, "outputs/step81_artifact_manifest/artifact_summary.json", "step81_vtr_count"),
        "step82_step81_regression_guard_pass": False,
    }
    summary["step82_step81_regression_guard_pass"] = bool(
        rows
        and summary["pass_count"] == summary["row_count"]
        and summary["artifact_pass_count"] == summary["artifact_check_count"]
        and summary["step81_activation_feature_count"] == 0
        and summary["planned_step82_activation_feature_count"] == 1
        and summary["step81_driver_run_dir_count"] == 0
        and summary["step81_vtr_count"] == 0
        and summary["step81_particle_npy_count"] == 0
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
