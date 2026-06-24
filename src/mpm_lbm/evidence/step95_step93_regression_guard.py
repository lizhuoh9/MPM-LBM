from __future__ import annotations

import json
from pathlib import Path


def build_step95_step93_regression_guard(
    root: Path,
    policy_path: str = "configs/step95_step93_regression_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    rows = [artifact_row(root, check) for check in policy["artifact_checks"]]
    plan_summary = read_json(
        root / "outputs/step93_taichi_ggui_visualization_enablement_plan/taichi_ggui_visualization_enablement_plan.json"
    )["summary"]
    guard_summary = read_json(
        root / "outputs/step93_taichi_ggui_visualization_enablement_guard/taichi_ggui_visualization_enablement_guard.json"
    )["summary"]
    output_summary = read_json(root / "outputs/step93_output_guard/output_guard.json")["summary"]
    artifact_summary = read_json(root / "outputs/step93_artifact_manifest/artifact_summary.json")
    summary = {
        "artifact_check_count": len(policy["artifact_checks"]),
        "artifact_pass_count": sum(1 for row in rows if row["pass"]),
        "pass_count": sum(1 for row in rows if row["pass"]),
        "planned_step94_activation_feature_count": guard_summary["planned_step94_activation_feature_count"],
        "row_count": len(rows),
        "step93_activation_feature_count": plan_summary["step93_activation_feature_count"],
        "step93_artifact_budget_pass": artifact_summary["artifact_budget_pass"],
        "step93_driver_run_dir_count": output_summary["step93_driver_run_dir_count"],
        "step93_ggui_screenshot_count": output_summary["step93_ggui_screenshot_count"],
        "step93_output_guard_pass": output_summary["output_guard_pass"],
        "step93_particle_npy_count": output_summary["step93_particle_npy_count"],
        "step93_step90_regression_guard_pass": artifact_value(
            root, "outputs/step93_step90_regression_guard/step90_regression_guard.json", "step93_step90_regression_guard_pass"
        ),
        "step93_step91_regression_guard_pass": artifact_value(
            root, "outputs/step93_step91_regression_guard/step91_regression_guard.json", "step93_step91_regression_guard_pass"
        ),
        "step93_step92_regression_guard_pass": artifact_value(
            root, "outputs/step93_step92_regression_guard/step92_regression_guard.json", "step93_step92_regression_guard_pass"
        ),
        "step93_taichi_ggui_visualization_enablement_guard_pass": guard_summary[
            "step93_taichi_ggui_visualization_enablement_guard_pass"
        ],
        "step93_taichi_ggui_visualization_enablement_plan_pass": plan_summary[
            "step93_taichi_ggui_visualization_enablement_plan_pass"
        ],
        "step95_step93_regression_guard_pass": False,
        "vtr_file_count": output_summary["vtr_file_count"],
    }
    summary["step95_step93_regression_guard_pass"] = bool(
        rows
        and summary["artifact_pass_count"] == summary["artifact_check_count"]
        and summary["step93_taichi_ggui_visualization_enablement_plan_pass"] is True
        and summary["step93_taichi_ggui_visualization_enablement_guard_pass"] is True
        and summary["step93_step92_regression_guard_pass"] is True
        and summary["step93_step91_regression_guard_pass"] is True
        and summary["step93_step90_regression_guard_pass"] is True
        and summary["step93_output_guard_pass"] is True
        and summary["step93_artifact_budget_pass"] is True
        and summary["step93_activation_feature_count"] == int(policy["expected_step93_activation_feature_count"])
        and summary["planned_step94_activation_feature_count"]
        == int(policy["expected_planned_step94_activation_feature_count"])
        and summary["step93_driver_run_dir_count"] == int(policy["expected_step93_driver_run_dir_count"])
        and summary["step93_ggui_screenshot_count"] == int(policy["expected_step93_ggui_screenshot_count"])
        and summary["step93_particle_npy_count"] == int(policy["expected_step93_particle_npy_count"])
        and summary["vtr_file_count"] == int(policy["expected_vtr_file_count"])
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
