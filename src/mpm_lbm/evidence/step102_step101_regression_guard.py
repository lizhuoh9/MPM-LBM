from __future__ import annotations

import json
from pathlib import Path


def build_step102_step101_regression_guard(
    root: Path,
    policy_path: str = "configs/step102_step101_regression_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    rows = [artifact_row(root, check) for check in policy["artifact_checks"]]
    output_summary = read_json(root / "outputs/step101_output_guard/output_guard.json")["summary"]
    artifact_summary = read_json(root / "outputs/step101_artifact_manifest/artifact_summary.json")
    summary = {
        "artifact_check_count": len(policy["artifact_checks"]),
        "artifact_pass_count": sum(1 for row in rows if row["pass"]),
        "pass_count": sum(1 for row in rows if row["pass"]),
        "row_count": len(rows),
        "step101_48cube_10step_taichi_ggui_visualization_guard_pass": artifact_value(
            root,
            "outputs/step101_48cube_10step_taichi_ggui_visualization_guard/48cube_10step_taichi_ggui_visualization_guard.json",
            "step101_48cube_10step_taichi_ggui_visualization_guard_pass",
        ),
        "step101_48cube_10step_taichi_ggui_visualization_plan_pass": artifact_value(
            root,
            "outputs/step101_48cube_10step_taichi_ggui_visualization_plan/48cube_10step_taichi_ggui_visualization_plan.json",
            "step101_48cube_10step_taichi_ggui_visualization_plan_pass",
        ),
        "step101_artifact_budget_pass": artifact_summary["artifact_budget_pass"],
        "step101_driver_run_dir_count": output_summary["step101_driver_run_dir_count"],
        "step101_ggui_screenshot_count": output_summary["step101_ggui_screenshot_count"],
        "step101_output_guard_pass": output_summary["output_guard_pass"],
        "step101_particle_npy_count": output_summary["step101_particle_npy_count"],
        "step101_vtr_count": output_summary["step101_vtr_count"],
        "step102_step101_regression_guard_pass": False,
    }
    summary["step102_step101_regression_guard_pass"] = bool(
        rows
        and summary["artifact_pass_count"] == summary["artifact_check_count"]
        and summary["step101_48cube_10step_taichi_ggui_visualization_plan_pass"] is True
        and summary["step101_48cube_10step_taichi_ggui_visualization_guard_pass"] is True
        and summary["step101_output_guard_pass"] is True
        and summary["step101_artifact_budget_pass"] is True
        and summary["step101_driver_run_dir_count"] == int(policy["expected_step101_driver_run_dir_count"])
        and summary["step101_ggui_screenshot_count"] == int(policy["expected_step101_ggui_screenshot_count"])
        and summary["step101_vtr_count"] == int(policy["expected_step101_vtr_count"])
        and summary["step101_particle_npy_count"] == int(policy["expected_step101_particle_npy_count"])
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
