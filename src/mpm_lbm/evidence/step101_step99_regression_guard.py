from __future__ import annotations

import json
from pathlib import Path


def build_step101_step99_regression_guard(
    root: Path,
    policy_path: str = "configs/step101_step99_regression_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    rows = [artifact_row(root, check) for check in policy["artifact_checks"]]
    plan_summary = read_json(
        root
        / "outputs/step99_48cube_5step_taichi_ggui_visualization_plan/"
        / "48cube_5step_taichi_ggui_visualization_plan.json"
    )["summary"]
    guard_summary = read_json(
        root
        / "outputs/step99_48cube_5step_taichi_ggui_visualization_guard/"
        / "48cube_5step_taichi_ggui_visualization_guard.json"
    )["summary"]
    output_summary = read_json(root / "outputs/step99_output_guard/output_guard.json")["summary"]
    artifact_summary = read_json(root / "outputs/step99_artifact_manifest/artifact_summary.json")
    summary = {
        "artifact_check_count": len(policy["artifact_checks"]),
        "artifact_pass_count": sum(1 for row in rows if row["pass"]),
        "pass_count": sum(1 for row in rows if row["pass"]),
        "planned_step100_activation_feature_count": plan_summary["planned_step100_activation_feature_count"],
        "row_count": len(rows),
        "step101_step99_regression_guard_pass": False,
        "step99_48cube_5step_taichi_ggui_visualization_guard_pass": guard_summary[
            "step99_48cube_5step_taichi_ggui_visualization_guard_pass"
        ],
        "step99_48cube_5step_taichi_ggui_visualization_plan_pass": plan_summary[
            "step99_48cube_5step_taichi_ggui_visualization_plan_pass"
        ],
        "step99_activation_feature_count": plan_summary["step99_activation_feature_count"],
        "step99_artifact_budget_pass": artifact_summary["artifact_budget_pass"],
        "step99_driver_run_dir_count": output_summary["step99_driver_run_dir_count"],
        "step99_ggui_screenshot_count": output_summary["step99_ggui_screenshot_count"],
        "step99_ggui_video_count": output_summary["step99_ggui_video_count"],
        "step99_output_guard_pass": output_summary["output_guard_pass"],
        "step99_particle_npy_count": output_summary["step99_particle_npy_count"],
        "step99_step96_regression_guard_pass": artifact_value(
            root,
            "outputs/step99_step96_regression_guard/step96_regression_guard.json",
            "step99_step96_regression_guard_pass",
        ),
        "step99_step97_regression_guard_pass": artifact_value(
            root,
            "outputs/step99_step97_regression_guard/step97_regression_guard.json",
            "step99_step97_regression_guard_pass",
        ),
        "step99_step98_regression_guard_pass": artifact_value(
            root,
            "outputs/step99_step98_regression_guard/step98_regression_guard.json",
            "step99_step98_regression_guard_pass",
        ),
        "step99_vtr_count": output_summary["step99_vtr_count"],
    }
    summary["step101_step99_regression_guard_pass"] = bool(
        rows
        and summary["artifact_pass_count"] == summary["artifact_check_count"]
        and summary["step99_48cube_5step_taichi_ggui_visualization_plan_pass"] is True
        and summary["step99_48cube_5step_taichi_ggui_visualization_guard_pass"] is True
        and summary["step99_step98_regression_guard_pass"] is True
        and summary["step99_step97_regression_guard_pass"] is True
        and summary["step99_step96_regression_guard_pass"] is True
        and summary["step99_output_guard_pass"] is True
        and summary["step99_artifact_budget_pass"] is True
        and summary["step99_activation_feature_count"] == int(policy["expected_step99_activation_feature_count"])
        and summary["planned_step100_activation_feature_count"]
        == int(policy["expected_planned_step100_activation_feature_count"])
        and summary["step99_driver_run_dir_count"] == int(policy["expected_step99_driver_run_dir_count"])
        and summary["step99_ggui_screenshot_count"] == int(policy["expected_step99_ggui_screenshot_count"])
        and summary["step99_ggui_video_count"] == int(policy["expected_step99_ggui_video_count"])
        and summary["step99_vtr_count"] == int(policy["expected_step99_vtr_count"])
        and summary["step99_particle_npy_count"] == int(policy["expected_step99_particle_npy_count"])
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
