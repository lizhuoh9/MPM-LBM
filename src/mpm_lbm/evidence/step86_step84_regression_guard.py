from __future__ import annotations

import json
from pathlib import Path


def build_step86_step84_regression_guard(
    root: Path,
    policy_path: str = "configs/step86_step84_regression_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    rows = [artifact_row(root, check) for check in policy["artifact_checks"]]
    smoke_summary = read_json(
        root
        / "outputs/step84_runtime_geometry_wall_velocity_combined_smoke_matrix/runtime_geometry_wall_velocity_combined_smoke_matrix.json"
    )["summary"]
    output_summary = read_json(root / "outputs/step84_output_guard/output_guard.json")["summary"]
    summary = {
        "artifact_check_count": len(policy["artifact_checks"]),
        "artifact_pass_count": sum(1 for row in rows if row["pass"]),
        "pass_count": sum(1 for row in rows if row["pass"]),
        "row_count": len(rows),
        "step84_activation_feature_count": smoke_summary["activation_feature_count"],
        "step84_combined_runtime_geometry_wall_velocity_enabled_count": smoke_summary[
            "combined_runtime_geometry_wall_velocity_enabled_count"
        ],
        "step84_output_guard_pass": output_summary["output_guard_pass"],
        "step84_particle_npy_count": output_summary["step84_particle_npy_count"],
        "step84_runtime_geometry_enabled_count": smoke_summary["runtime_geometry_enabled_count"],
        "step84_runtime_geometry_wall_velocity_combined_quality_pass": artifact_value(
            root,
            "outputs/step84_runtime_geometry_wall_velocity_combined_quality/runtime_geometry_wall_velocity_combined_quality.json",
            "step84_runtime_geometry_wall_velocity_combined_quality_pass",
        ),
        "step84_runtime_geometry_wall_velocity_combined_smoke_matrix_pass": smoke_summary[
            "step84_runtime_geometry_wall_velocity_combined_smoke_matrix_pass"
        ],
        "step84_squid_proxy_enabled_count": smoke_summary["squid_proxy_enabled_count"],
        "step84_vtr_count": output_summary["step84_vtr_count"],
        "step84_wall_velocity_enabled_count": smoke_summary["wall_velocity_enabled_count"],
        "step86_step84_regression_guard_pass": False,
    }
    summary["step86_step84_regression_guard_pass"] = bool(
        rows
        and summary["artifact_pass_count"] == summary["artifact_check_count"]
        and summary["step84_activation_feature_count"] == int(policy["expected_activation_feature_count"])
        and summary["step84_runtime_geometry_enabled_count"] == int(policy["expected_runtime_geometry_enabled_count"])
        and summary["step84_wall_velocity_enabled_count"] == int(policy["expected_wall_velocity_enabled_count"])
        and summary["step84_combined_runtime_geometry_wall_velocity_enabled_count"]
        == int(policy["expected_combined_runtime_geometry_wall_velocity_enabled_count"])
        and summary["step84_squid_proxy_enabled_count"] == 0
        and summary["step84_vtr_count"] == 0
        and summary["step84_particle_npy_count"] == 0
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
