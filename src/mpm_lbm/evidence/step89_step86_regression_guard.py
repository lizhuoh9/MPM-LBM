from __future__ import annotations

import json
from pathlib import Path


def build_step89_step86_regression_guard(
    root: Path,
    policy_path: str = "configs/step89_step86_regression_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    rows = [artifact_row(root, check) for check in policy["artifact_checks"]]
    smoke_summary = read_json(
        root / "outputs/step86_squid_proxy_static_geometry_smoke_matrix/squid_proxy_static_geometry_smoke_matrix.json"
    )["summary"]
    output_summary = read_json(root / "outputs/step86_output_guard/output_guard.json")["summary"]
    artifact_summary = read_json(root / "outputs/step86_artifact_manifest/artifact_summary.json")
    summary = {
        "artifact_check_count": len(policy["artifact_checks"]),
        "artifact_pass_count": sum(1 for row in rows if row["pass"]),
        "pass_count": sum(1 for row in rows if row["pass"]),
        "row_count": len(rows),
        "step86_activation_feature_count": smoke_summary["activation_feature_count"],
        "step86_artifact_budget_pass": artifact_summary["artifact_budget_pass"],
        "step86_particle_npy_count": output_summary["step86_particle_npy_count"],
        "step86_runtime_geometry_enabled_count": smoke_summary["runtime_geometry_enabled_count"],
        "step86_squid_proxy_enabled_count": smoke_summary["squid_proxy_enabled_count"],
        "step86_vtr_count": output_summary["step86_vtr_count"],
        "step86_wall_velocity_enabled_count": smoke_summary["wall_velocity_enabled_count"],
        "step89_step86_regression_guard_pass": False,
    }
    summary["step89_step86_regression_guard_pass"] = bool(
        rows
        and summary["artifact_pass_count"] == summary["artifact_check_count"]
        and summary["step86_artifact_budget_pass"] is True
        and summary["step86_activation_feature_count"] == int(policy["expected_step86_activation_feature_count"])
        and summary["step86_squid_proxy_enabled_count"] == int(policy["expected_step86_squid_proxy_enabled_count"])
        and summary["step86_runtime_geometry_enabled_count"]
        == int(policy["expected_step86_runtime_geometry_enabled_count"])
        and summary["step86_wall_velocity_enabled_count"] == int(policy["expected_step86_wall_velocity_enabled_count"])
        and summary["step86_vtr_count"] == int(policy["expected_step86_vtr_count"])
        and summary["step86_particle_npy_count"] == int(policy["expected_step86_particle_npy_count"])
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
