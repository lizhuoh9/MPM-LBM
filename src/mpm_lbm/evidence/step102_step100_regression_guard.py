from __future__ import annotations

import json
from pathlib import Path


def build_step102_step100_regression_guard(
    root: Path,
    policy_path: str = "configs/step102_step100_regression_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    rows = [artifact_row(root, check) for check in policy["artifact_checks"]]
    matrix_summary = read_json(
        root
        / "outputs/step100_48cube_5step_taichi_ggui_visualization_run_matrix/"
        / "48cube_5step_taichi_ggui_visualization_run_matrix.json"
    )["summary"]
    quality_summary = read_json(
        root
        / "outputs/step100_48cube_5step_taichi_ggui_visualization_quality/"
        / "48cube_5step_taichi_ggui_visualization_quality.json"
    )["summary"]
    activation_summary = read_json(root / "outputs/step100_activation_guard/activation_guard.json")["summary"]
    output_summary = read_json(root / "outputs/step100_output_guard/output_guard.json")["summary"]
    artifact_summary = read_json(root / "outputs/step100_artifact_manifest/artifact_summary.json")
    summary = {
        "artifact_check_count": len(policy["artifact_checks"]),
        "artifact_pass_count": sum(1 for row in rows if row["pass"]),
        "pass_count": sum(1 for row in rows if row["pass"]),
        "row_count": len(rows),
        "step100_48cube_5step_taichi_ggui_visualization_quality_pass": quality_summary[
            "step100_48cube_5step_taichi_ggui_visualization_quality_pass"
        ],
        "step100_48cube_5step_taichi_ggui_visualization_run_matrix_pass": matrix_summary[
            "step100_48cube_5step_taichi_ggui_visualization_run_matrix_pass"
        ],
        "step100_activation_guard_pass": activation_summary["step100_activation_guard_pass"],
        "step100_artifact_budget_pass": artifact_summary["artifact_budget_pass"],
        "step100_completed_lbm_steps": matrix_summary["min_completed_lbm_steps"],
        "step100_ggui_screenshot_count": output_summary["step100_ggui_screenshot_count"],
        "step100_n_grid": matrix_summary["step100_n_grid"],
        "step100_output_guard_pass": output_summary["output_guard_pass"],
        "step100_particle_npy_count": output_summary["step100_particle_npy_count"],
        "step100_vtr_count": output_summary["step100_vtr_count"],
        "step102_step100_regression_guard_pass": False,
    }
    summary["step102_step100_regression_guard_pass"] = bool(
        rows
        and summary["artifact_pass_count"] == summary["artifact_check_count"]
        and summary["step100_48cube_5step_taichi_ggui_visualization_run_matrix_pass"] is True
        and summary["step100_48cube_5step_taichi_ggui_visualization_quality_pass"] is True
        and summary["step100_activation_guard_pass"] is True
        and summary["step100_output_guard_pass"] is True
        and summary["step100_artifact_budget_pass"] is True
        and summary["step100_completed_lbm_steps"] == int(policy["expected_step100_completed_lbm_steps"])
        and summary["step100_n_grid"] == int(policy["expected_step100_n_grid"])
        and summary["step100_ggui_screenshot_count"] == int(policy["expected_step100_ggui_screenshot_count"])
        and summary["step100_vtr_count"] == int(policy["expected_step100_vtr_count"])
        and summary["step100_particle_npy_count"] == int(policy["expected_step100_particle_npy_count"])
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
