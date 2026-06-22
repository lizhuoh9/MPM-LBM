from __future__ import annotations

import json
from pathlib import Path


def build_step86_step85_regression_guard(
    root: Path,
    policy_path: str = "configs/step86_step85_regression_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    rows = [artifact_row(root, check) for check in policy["artifact_checks"]]
    plan_summary = read_json(
        root / "outputs/step85_squid_proxy_static_geometry_activation_plan/squid_proxy_static_geometry_activation_plan.json"
    )["summary"]
    manifest_summary = read_json(root / "outputs/step85_artifact_manifest/artifact_summary.json")
    summary = {
        "artifact_check_count": len(policy["artifact_checks"]),
        "artifact_pass_count": sum(1 for row in rows if row["pass"]),
        "pass_count": sum(1 for row in rows if row["pass"]),
        "planned_step86_activation_feature_count": plan_summary["planned_step86_activation_feature_count"],
        "row_count": len(rows),
        "step85_activation_feature_count": plan_summary["step85_activation_feature_count"],
        "step85_artifact_budget_pass": manifest_summary["artifact_budget_pass"],
        "step85_driver_run_dir_count": manifest_summary["step85_driver_run_dir_count"],
        "step85_particle_npy_count": manifest_summary["step85_particle_npy_count"],
        "step85_squid_proxy_static_geometry_activation_guard_pass": artifact_value(
            root,
            "outputs/step85_squid_proxy_static_geometry_activation_guard/squid_proxy_static_geometry_activation_guard.json",
            "step85_squid_proxy_static_geometry_activation_guard_pass",
        ),
        "step85_squid_proxy_static_geometry_activation_plan_pass": plan_summary[
            "step85_squid_proxy_static_geometry_activation_plan_pass"
        ],
        "step85_step31_reference_guard_pass": artifact_value(
            root, "outputs/step85_step31_reference_guard/step31_reference_guard.json", "step85_step31_reference_guard_pass"
        ),
        "step85_step84_regression_guard_pass": artifact_value(
            root, "outputs/step85_step84_regression_guard/step84_regression_guard.json", "step85_step84_regression_guard_pass"
        ),
        "step85_vtr_count": manifest_summary["step85_vtr_count"],
        "step86_step85_regression_guard_pass": False,
    }
    summary["step86_step85_regression_guard_pass"] = bool(
        rows
        and summary["artifact_pass_count"] == summary["artifact_check_count"]
        and summary["step85_activation_feature_count"] == int(policy["expected_step85_activation_feature_count"])
        and summary["planned_step86_activation_feature_count"] == int(policy["expected_planned_step86_activation_feature_count"])
        and summary["step85_driver_run_dir_count"] == 0
        and summary["step85_vtr_count"] == 0
        and summary["step85_particle_npy_count"] == 0
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
