from __future__ import annotations

import json
from pathlib import Path


def build_step84_step82_regression_guard(
    root: Path,
    policy_path: str = "configs/step84_step82_regression_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    rows = [artifact_row(root, check) for check in policy["artifact_checks"]]
    summary = {
        "artifact_check_count": len(policy["artifact_checks"]),
        "artifact_pass_count": sum(1 for row in rows if row["pass"]),
        "pass_count": sum(1 for row in rows if row["pass"]),
        "row_count": len(rows),
        "step82_activation_feature_count": artifact_value(
            root,
            "outputs/step82_wall_velocity_solid_vel_smoke_matrix/wall_velocity_solid_vel_smoke_matrix.json",
            "activation_feature_count",
        ),
        "step82_artifact_budget_pass": artifact_value(
            root, "outputs/step82_artifact_manifest/artifact_summary.json", "artifact_budget_pass"
        ),
        "step82_combined_runtime_geometry_wall_velocity_enabled_count": artifact_value(
            root,
            "outputs/step82_wall_velocity_solid_vel_smoke_matrix/wall_velocity_solid_vel_smoke_matrix.json",
            "combined_runtime_geometry_wall_velocity_enabled_count",
        ),
        "step82_particle_npy_count": artifact_value(
            root, "outputs/step82_artifact_manifest/artifact_summary.json", "step82_particle_npy_count"
        ),
        "step82_runtime_geometry_enabled_count": artifact_value(
            root,
            "outputs/step82_wall_velocity_solid_vel_smoke_matrix/wall_velocity_solid_vel_smoke_matrix.json",
            "runtime_geometry_enabled_count",
        ),
        "step82_vtr_count": artifact_value(root, "outputs/step82_artifact_manifest/artifact_summary.json", "step82_vtr_count"),
        "step82_wall_velocity_enabled_count": artifact_value(
            root,
            "outputs/step82_wall_velocity_solid_vel_smoke_matrix/wall_velocity_solid_vel_smoke_matrix.json",
            "wall_velocity_enabled_count",
        ),
        "step84_step82_regression_guard_pass": False,
    }
    summary["step84_step82_regression_guard_pass"] = bool(
        rows
        and summary["pass_count"] == summary["row_count"]
        and summary["artifact_pass_count"] == summary["artifact_check_count"]
        and summary["step82_activation_feature_count"] == 1
        and summary["step82_wall_velocity_enabled_count"] == 1
        and summary["step82_runtime_geometry_enabled_count"] == 0
        and summary["step82_combined_runtime_geometry_wall_velocity_enabled_count"] == 0
        and summary["step82_vtr_count"] == 0
        and summary["step82_particle_npy_count"] == 0
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
